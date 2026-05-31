import os
import json
from pathlib import Path
import datetime
import pdfplumber

from notanegociacao.notanegociacao import NotaNegociacao
from notanegociacao.util import CustomEncoder, from_dict

NOTAS_DIR = './notas'
NOTAS_FILE = 'notas.json'


class Corretora:
    notasNegociacao: list[NotaNegociacao]

    def __init__(self, dir: str | None = None):
        if (dir != None):
            self.notasNegociacao = self.lerNotasDiretorio(dir)

    def lerNotasDiretorio(self, dir: str) -> list[NotaNegociacao]:
        result = self.getNotasFromJson()

        try:
            notasPdf = sorted(
                [f for f in os.listdir(dir) if f.endswith('.pdf')])

            pdfCount = 1

            for pdf in notasPdf:
                # Extract date from filename (format: NotaNegociacao_48055_20250404.pdf)
                pdf_date_str = pdf.split('_')[-1].replace('.pdf', '')
                pdf_date = datetime.datetime.strptime(
                    pdf_date_str, '%Y%m%d').date()

                date_exists = any(nota.dataPregao ==
                                  pdf_date for nota in result)

                if date_exists:
                    print(f'{pdf} já processada')
                    pdfCount += 1
                    continue

                with pdfplumber.open(dir + pdf) as pdfFile:
                    print(f'Processando PDFs: {pdfCount}/{len(notasPdf)}')
                    print(pdf)
                    pdfCount += 1

                    for page in pdfFile.pages:
                        result = NotaNegociacao.parseText(
                            page.extract_text(), result)
        finally:
            result = sorted(result, key=lambda r: r.dataPregao)
            self.saveNotasJson(result)

        return result

    def getNotasFromJson(self) -> list[NotaNegociacao]:
        notas_file = self.getJsonPath()

        result: list[NotaNegociacao] = []
        if notas_file.exists():
            with open(notas_file, 'r') as f:
                try:
                    result = json.load(f)
                    result = [from_dict(data, NotaNegociacao)
                              for data in result]
                except json.JSONDecodeError:
                    result = []

        return result

    def saveNotasJson(self, notas: list[NotaNegociacao]) -> None:
        notas_file = self.getJsonPath()
        with open(notas_file, 'w') as f:
            json.dump(notas, f, cls=CustomEncoder, ensure_ascii=False)

    def getJsonPath(self) -> Path:
        notas_dir = Path(NOTAS_DIR)
        notas_dir.mkdir(exist_ok=True)

        return notas_dir / NOTAS_FILE
