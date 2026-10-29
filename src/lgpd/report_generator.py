"""
LGPD Article 18 PDF Report Generator.
Generates official data subject access reports in compliance with LGPD (Lei 13.709/2018).
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from fpdf import FPDF


class LGPDReportGenerator(FPDF):
    """Custom FPDF generator for LGPD Art. 18 Reports."""

    def __init__(self, user_data: Dict[str, Any]):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.user_data = user_data
        self.generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.set_auto_page_break(auto=True, margin=15)

    def header(self) -> None:
        """Header rendered on every page."""
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Data Broker Opt-Out Bot - Relatorio LGPD (Art. 18)", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
        self.line(10, 18, 200, 18)
        self.ln(4)

    def footer(self) -> None:
        """Footer rendered on every page."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        page_str = f"Pagina {self.page_no()} | Gerado em {self.generated_at}"
        self.cell(0, 10, page_str, align="C")

    def chapter_title(self, title: str) -> None:
        """Section header."""
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(20, 40, 80)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_paragraph(self, text: str) -> None:
        """Body text formatting."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(2)


def generate_lgpd_report(user_data: Dict[str, Any], output_path: str) -> str:
    """
    Generates a PDF report fulfilling LGPD Article 18 rights.

    :param user_data: Dictionary containing user details and request history.
    :param output_path: Path where the PDF file will be saved.
    :return: Absolute path to the generated PDF report.
    """
    pdf = LGPDReportGenerator(user_data)
    pdf.add_page()

    # Document Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(10, 30, 70)
    pdf.cell(0, 10, "Relatorio de Direitos do Titular de Dados", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, "Lei Geral de Protecao de Dados (LGPD - Lei n. 13.709/2018, Art. 18)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    # Section 1: Identification
    pdf.chapter_title("1. Identificacao do Titular e do Requerimento")
    user_id = str(user_data.get("user_id", "N/A"))
    name = str(user_data.get("name", "N/A"))
    email = str(user_data.get("email", "N/A"))
    cpf = str(user_data.get("cpf", "N/A"))

    info_text = (
        f"- ID Telegram / Usuario: {user_id}\n"
        f"- Nome do Titular: {name}\n"
        f"- E-mail cadastrado: {email}\n"
        f"- CPF (mascarado/parcial): {cpf}\n"
        f"- Data da Solicitacao: {pdf.generated_at}"
    )
    pdf.body_paragraph(info_text)

    # Section 2: Article 18 Rights Declaration
    pdf.chapter_title("2. Declaracao de Tratamento e Direitos (Art. 18 LGPD)")

    rights_summary = (
        "Em conformidade com o Artigo 18 da Lei n. 13.709/2018 (LGPD), este documento "
        "atesta o atendimento aos direitos do titular:\n"
        "1. Confirmacao de Tratamento (Art. 18, I): Confirmamos que tratamos seus dados estritamente "
        "para automatizar e acompanhar solicitacoes de opt-out/exclusao junto a Data Brokers.\n"
        "2. Acesso aos Dados (Art. 18, II): Todos os dados sob posse do bot e historico de solicitacoes "
        "estao detalhados neste relatorio.\n"
        "3. Correcao e Atualizacao (Art. 18, III): O titular pode atualizar seus dados cadastrais diretamente "
        "pelo bot Telegram a qualquer momento.\n"
        "4. Anonimizacao / Eliminacao (Art. 18, IV e VI): Os dados sao retidos estritamente durante o "
        "processamento e sao eliminados mediante solicitacao expressa do titular.\n"
        "5. Portabilidade (Art. 18, V): Este relatorio serve como extrato estruturado das operacoes realizadas.\n"
        "6. Compartilhamento (Art. 18, VII): Os dados do titular sao transmitidos exclusivamente aos "
        "Data Brokers selecionados para efetivacao das solicitacoes de opt-out.\n"
        "7. Consentimento e Revogacao (Art. 18, VIII e IX): O consentimento foi fornecido na inicializacao "
        "do bot e pode ser revogado a qualquer momento via comando de cancelamento."
    )
    pdf.body_paragraph(rights_summary)

    # Section 3: Data Brokers Request History
    pdf.chapter_title("3. Historico de Solicitacoes de Opt-Out / Exclusao")
    requests: List[Dict[str, Any]] = user_data.get("requests", [])

    if not requests:
        pdf.body_paragraph("Nenhuma solicitacao de opt-out registrada ate o momento.")
    else:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 225, 235)
        # Table Header
        pdf.cell(50, 7, "Data Broker", border=1, fill=True)
        pdf.cell(35, 7, "Data Env.", border=1, fill=True)
        pdf.cell(35, 7, "Status", border=1, fill=True)
        pdf.cell(70, 7, "Protocolo / Ref.", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        for req in requests:
            broker = str(req.get("broker", "N/A"))[:25]
            date_req = str(req.get("date", "N/A"))[:18]
            status = str(req.get("status", "Pendente"))[:18]
            protocol = str(req.get("protocol", "N/A"))[:35]

            pdf.cell(50, 6, broker, border=1)
            pdf.cell(35, 6, date_req, border=1)
            pdf.cell(35, 6, status, border=1)
            pdf.cell(70, 6, protocol, border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Output save
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    pdf.output(output_path)
    return os.path.abspath(output_path)
