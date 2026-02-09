from .base import BaseResumeParser, ParserInput
from PIL import Image
import io
import fitz
from src.infrastructure.logger import get_app_logger
from src.agents.resume import get_resume_parse_agent, OutResumeParse
from src.infrastructure.exceptions import ParserError, TooManyPagesError, NotAResumeError
from pydantic_ai import BinaryContent
import time
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

        parsed_data = await self._run_agent(images)

        if not parsed_data.is_resume:
            raise NotAResumeError("Этот документ не похож на резюме")

        return parsed_data

    def _pdf_to_images(self, source: io.BytesIO, dpi: int = 200) -> list[Image.Image]:
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

    async def _run_agent(self, images: list[Image.Image]) -> OutResumeParse:

        start_total = time.perf_counter()
        logger.info("Starting agent run, images=%d", len(images))

        prompt_parts = [
            "Please extract all text and analyze the following resume screenshots:"
        ]

        # --- Подготовка изображений ---
        start_images = time.perf_counter()

        for idx, img in enumerate(images, start=1):
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            img_bytes = img_byte_arr.getvalue()

            prompt_parts.append(
                BinaryContent(
                    data=img_bytes,
                    media_type="image/png",
                )
            )

            logger.debug(
                "Prepared image %d: size=%.2f KB",
                idx,
                len(img_bytes) / 1024,
            )

        images_time = time.perf_counter() - start_images
        logger.info("Images prepared in %.3f s", images_time)

        # --- Вызов агента ---
        start_agent = time.perf_counter()

        result = await self._agent.run(user_prompt=prompt_parts)

        agent_time = time.perf_counter() - start_agent
        logger.info("Agent run completed in %.3f s", agent_time)

        total_time = time.perf_counter() - start_total
        logger.info("Total _run_agent time: %.3f s", total_time)
        logger.info("RESULT: %s", result.output)

        return result.output
