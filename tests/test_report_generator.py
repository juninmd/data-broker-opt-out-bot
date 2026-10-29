"""
Unit tests for LGPD PDF report generator.
"""
import os
import tempfile
import pytest
from pypdf import PdfReader
from src.lgpd.report_generator import generate_lgpd_report


def test_generate_lgpd_report_success():
    sample_data = {
        "user_id": 998877,
        "name": "Maria Oliveira",
        "email": "maria@exemplo.com.br",
        "cpf": "***.123.456-**",
        "requests": [
            {
                "broker": "Serasa Experian",
                "date": "01/10/2026 10:00",
                "status": "Concluido",
                "protocol": "SER-123456",
            },
            {
                "broker": "Boa Vista",
                "date": "02/10/2026 14:30",
                "status": "Pendente",
                "protocol": "BVA-789012",
            },
        ],
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_pdf = os.path.join(tmp_dir, "lgpd_report_test.pdf")
        result_path = generate_lgpd_report(sample_data, output_pdf)

        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 0

        reader = PdfReader(result_path)
        assert len(reader.pages) >= 1

        first_page_text = reader.pages[0].extract_text()
        assert "Relatorio de Direitos do Titular de Dados" in first_page_text
        assert "Maria Oliveira" in first_page_text
        assert "998877" in first_page_text
        assert "Serasa Experian" in first_page_text
        assert "SER-123456" in first_page_text


def test_generate_lgpd_report_empty_requests():
    sample_data = {
        "user_id": 111,
        "name": "Carlos Souza",
        "email": "carlos@exemplo.com.br",
        "cpf": "N/A",
        "requests": [],
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_pdf = os.path.join(tmp_dir, "lgpd_report_empty.pdf")
        result_path = generate_lgpd_report(sample_data, output_pdf)

        assert os.path.exists(result_path)
        reader = PdfReader(result_path)
        first_page_text = reader.pages[0].extract_text()
        assert "Nenhuma solicitacao de opt-out registrada ate o momento." in first_page_text
