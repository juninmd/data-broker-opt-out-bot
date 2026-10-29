/**
 * Validates a Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica) number using modulo 11 checksum algorithm.
 */
export function isValidCNPJ(cnpj: string): boolean {
  if (!cnpj) return false;

  // Clean non-digit characters
  const cleaned = cnpj.replace(/\D/g, '');

  if (cleaned.length !== 14) return false;

  // Reject known invalid repetitive sequences (e.g., 00000000000000, 11111111111111, etc.)
  if (/^(\d)\1{13}$/.test(cleaned)) return false;

  const digits = cleaned.split('').map(Number);

  // Validate 1st digit
  const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  let sum = 0;
  for (let i = 0; i < 12; i++) {
    sum += digits[i] * weights1[i];
  }
  let rem = sum % 11;
  const expectedDigit1 = rem < 2 ? 0 : 11 - rem;
  if (digits[12] !== expectedDigit1) return false;

  // Validate 2nd digit
  const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  sum = 0;
  for (let i = 0; i < 13; i++) {
    sum += digits[i] * weights2[i];
  }
  rem = sum % 11;
  const expectedDigit2 = rem < 2 ? 0 : 11 - rem;
  if (digits[13] !== expectedDigit2) return false;

  return true;
}

export function formatCNPJ(cnpj: string): string {
  const cleaned = cnpj.replace(/\D/g, '');
  if (cleaned.length !== 14) return cnpj;
  return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}
