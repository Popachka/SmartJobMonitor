import io
from datetime import datetime

import fitz
from PIL import Image
from pydantic_ai import BinaryContent

from app.application.dto import OutResumeParse
from app.core.logger import get_app_logger
from app.infrastructure.llm_provider import get_resume_parse_agent
from app.infrastructure.parsers.base import BaseResumeParser, ParserInput
from app.infrastructure.parsers.exceptions import NotAResumeError, ParserError, TooManyPagesError

logger = get_app_logger(__name__)


class PDFParser(BaseResumeParser):
    def __init__(self) -> None:
        self._agent = get_resume_parse_agent()

    async def extract_text(self, source: ParserInput) -> OutResumeParse:
        if not isinstance(source, io.BytesIO):
            raise ParserError(f"PDFParser ожидает BytesIO, получен {type(source)}")
        logger.info("Resume parsing started")
        images, pdf_text = self._pdf_to_images_and_text(source)

        if not images:
            raise ParserError("Не удалось получить изображения из PDF")
        if len(images) > 10:
            logger.warning("Resume rejected: too many pages (%d)", len(images))
            raise TooManyPagesError("Резюме слишком длинное (более 10 страниц)")

        try:
            logger.info("Resume images ready: %d pages", len(images))
            parsed_data = await self._run_agent(images, pdf_text)
        finally:
            for img in images:
                img.close()
            images.clear()

        if not parsed_data.is_resume:
            logger.info("Resume parsing completed: not a resume")
            raise NotAResumeError("Этот документ не похож на резюме")

        logger.info("Resume parsing completed: success")
        return parsed_data

    def _pdf_to_images_and_text(
        self, source: io.BytesIO, dpi: int = 150
    ) -> tuple[list[Image.Image], str]:
        source.seek(0)
        images: list[Image.Image] = []
        text_parts: list[str] = []

        try:
            with fitz.open(stream=source.read(), filetype="pdf") as doc:
                for page in doc:
                    img = self._render_page(page, dpi)
                    if img:
                        images.append(img)
                    text_parts.append(page.get_text("text"))
        except (fitz.FileDataError, fitz.EmptyFileError) as exc:
            logger.error("Invalid PDF file: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error during PDF rendering: %s", exc)

        return images, "\n".join(part for part in text_parts if part)

    def _render_page(self, page: fitz.Page, dpi: int) -> Image.Image | None:
        try:
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            img.load()
            return img
        except Exception as exc:
            logger.error("Error rendering page %d: %s", page.number, exc)
            return None

    async def _run_agent(self, images: list[Image.Image], pdf_text: str) -> OutResumeParse:
        current_date = datetime.now().strftime("%B %Y")
        prompt_parts: list[str | BinaryContent] = [
            f"Текущая дата для расчётов: {current_date}\n"
            "Пожалуйста, извлеките весь текст и проанализируйте следующие данные резюме.\n\n"
            "Текстовый слой PDF (используй вместе со скриншотами):\n"
            f"{pdf_text}\n\n"
            "Скриншоты страниц резюме:"
        ]
        for idx, img in enumerate(images, start=1):
            image_to_use = img
            if img.mode in ("RGBA", "P"):
                image_to_use = img.convert("RGB")

            img_byte_arr = io.BytesIO()
            image_to_use.save(img_byte_arr, format="JPEG", quality=85, optimize=True)
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
            if image_to_use is not img:
                image_to_use.close()

        result = await self._agent.run(
            user_prompt=prompt_parts,
            metadata={"pipeline": "resume_parse"},
        )
        return result.output
