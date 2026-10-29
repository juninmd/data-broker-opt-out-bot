/**
 * Validates a Brazilian CPF (Cadastro de Pessoas Físicas) number using modulo 11 checksum algorithm.
 */
export function isValidCPF(cpf: string): boolean {
  if (!cpf) return false;

  // Clean non-digit characters
  const cleaned = cpf.replace(/\D/g, '');

  if (cleaned.length !== 11) return false;

  // Reject known invalid repetitive sequences (e.g., 00000000000, 11111111111, etc.)
  if (/^(\d)\1{10}$/.test(cleaned)) return false;

  const digits = cleaned.split('').map(Number);

  // Validate 1st digit
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += digits[i] * (10 - i);
  }
  let rem = sum % 11;
  const expectedDigit1 = rem < 2 ? 0 : 11 - rem;
  if (digits[9] !== expectedDigit1) return false;

  // Validate 2nd digit
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += digits[i] * (11 - i);
  }
  rem = sum % 11;
  const expectedDigit2 = rem < 2 ? 0 : 11 - rem;
  if (digits[10] !== expectedDigit2) return false;

  return true;
}

export function formatCPF(cpf: string): string {
  const cleaned = cpf.replace(/\D/g, '');
  if (cleaned.length !== 11) return cpf;
  return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}
