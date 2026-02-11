from .base import BaseResumeParser, ParserInput
from PIL import Image
import io
import fitz
from src.infrastructure.logger import get_app_logger, trace_performance
from src.infrastructure.agents.resume import get_resume_parse_agent, OutResumeParse
from src.infrastructure.exceptions import ParserError, TooManyPagesError, NotAResumeError
from pydantic_ai import BinaryContent
from datetime import datetime

logger = get_app_logger(__name__)


class PDFParser(BaseResumeParser):
    def __init__(self):
        self._agent = get_resume_parse_agent()

    async def extract_text(self, source: ParserInput) -> OutResumeParse:
        """Основной флоу: PDF -> Images -> Structured Data -> Text."""
        if not isinstance(source, io.BytesIO):
            raise ParserError(
                f"PDFParser ожидает BytesIO, получен {type(source)}")
        images = self._pdf_to_images(source)

        if not images:
            raise ParserError("Не удалось получить изображения из PDF")
        if len(images) > 10:
            raise TooManyPagesError(
                "Резюме слишком длинное (более 10 страниц)")

        try:
            parsed_data = await self._run_agent(images)
        finally:
            for img in images:
                img.close()
            images.clear()

        if not parsed_data.is_resume:
            raise NotAResumeError("Этот документ не похож на резюме")

        return parsed_data

    def _pdf_to_images(self, source: io.BytesIO, dpi: int = 150) -> list[Image.Image]:
        """Логика скриншотов страниц PDF."""
        source.seek(0)
        images: list[Image.Image] = []

        try:
            with fitz.open(stream=source.read(), filetype="pdf") as doc:
                for page in doc:
                    img = self._render_page(page, dpi)
                    if img:
                        images.append(img)
        except (fitz.FileDataError, fitz.EmptyFileError) as e:
            logger.error(f"Invalid PDF file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during PDF rendering: {e}")

        return images

    def _render_page(self, page: fitz.Page, dpi: int) -> Image.Image | None:
        """Рендеринг конкретной страницы в PIL.Image."""
        try:
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            img.load()
            return img
        except Exception as e:
            logger.error(f"Error rendering page {page.number}: {e}")
            return None

    @trace_performance("Send parse resume to agent")
    async def _run_agent(self, images: list[Image.Image]) -> OutResumeParse:
        current_date = datetime.now().strftime("%B %Y")
        prompt_parts = [
            f"Текущая дата для расчётов: {current_date}\n"
            "Пожалуйста, извлеките весь текст и проанализируйте следующие скриншоты резюме:"
        ]
        for idx, img in enumerate(images, start=1):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="JPEG", quality=85, optimize=True)
            img_bytes = img_byte_arr.getvalue()

            prompt_parts.append(
                BinaryContent(
                    data=img_bytes,
                    media_type="image/jpeg",
                )
            )

            logger.debug(
                "Подготовлено изображение %d: размер=%.2f КБ (JPEG)",
                idx,
                len(img_bytes) / 1024,
            )
            img_byte_arr.close()
        result = await self._agent.run(user_prompt=prompt_parts)
        return result.output
