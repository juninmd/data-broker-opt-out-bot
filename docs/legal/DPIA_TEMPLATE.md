# Relatório de Impacto à Proteção de Dados Pessoais (RIPD / DPIA)
**LGPD - Lei Geral de Proteção de Dados (Lei nº 13.709/2018, Artigo 38)**

---

## 1. Identificação do Agente e do Sistema
* **Nome do Sistema / Bot:** Data Broker Opt-Out Bot (`@data_broker_optout_bot`)
* **Controlador dos Dados:** [Nome da Organização / Controlador]
* **Encarregado pelo Tratamento de Dados (DPO):** [Nome do DPO] — `dpo@exemplo.com.br`
* **Data da Avaliação:** [Data de Emissão]
* **Versão do Documento:** 1.0

---

## 2. Descrição Geral do Tratamento de Dados Pessoais
O **Data Broker Opt-Out Bot** é uma ferramenta automatizada desenvolvida para auxiliar titulares de dados no exercício do seu direito de oposição e eliminação de dados pessoais mantidos por empresas *Data Brokers* (corretoras de dados) no Brasil e no exterior, nos termos do Artigo 18 da LGPD.

### 2.1 Categorias de Titulares
* Usuários finais do aplicativo Telegram que solicitam o envio de requerimentos de opt-out/exclusão de seus dados.

### 2.2 Categorias de Dados Tratados
* **Identificadores Pessoais:** Nome completo, CPF, e-mail, telefone, endereço residencial (estritamente os necessários solicitados pelas corretoras de dados para confirmação da identidade e localização dos registros a serem removidos).
* **Dados do Telegram:** Telegram User ID, Username.
* **Metadados de Requisições:** Status da solicitação (Pendente, Enviado, Concluído, Rejeitado), carimbo de data/hora (timestamps), comprovantes de envio e respostas recebidas dos Data Brokers.

### 2.3 Bases Legais do Tratamento (LGPD Art. 7º)
* **Execução de contrato / procedimentos preliminares (Art. 7º, V):** Prestação do serviço solicitado pelo próprio titular ao interagir com o bot.
* **Cumprimento de obrigação legal ou regulatória (Art. 7º, II):** Armazenamento de logs de auditoria e relatórios de conformidade.

---

## 3. Fluxo de Dados e Arquitetura do Sistema
1. **Coleta:** O titular fornece seus dados via interface do chat do Telegram diretamente ao bot.
2. **Processamento Local:** O bot valida os dados e prepara as requisições para os *Data Brokers* cadastrados via API pública ou automação via navegação headless.
3. **Transmissão aos Data Brokers:** As requisições de remoção/opt-out são submetidas formalmente aos canais oficiais de cada Data Broker.
4. **Armazenamento e Criptografia:** Os dados pessoais para solicitação são armazenados com criptografia em repouso (AES-256) e mantidos somente pelo período necessário para a conclusão das solicitações.
5. **Geração de Relatórios (Art. 18):** O bot gera relatórios em formato PDF (`/lgpd_report`) para prestação de contas ao titular.

---

## 4. Análise de Riscos à Proteção de Dados
| ID | Descrição do Risco | Nível de Impacto | Probabilidade | Nível do Risco |
|:---|:-------------------|:----------------:|:-------------:|:--------------:|
| R1 | Vazamento de dados durante a transmissão ao Data Broker | Alto | Baixa | Médio |
| R2 | Acesso não autorizado ao banco de dados do bot | Alto | Baixa | Médio |
| R3 | Interceptação de mensagens no Telegram | Médio | Baixa | Baixo |
| R4 | Armazenamento excessivo de dados pós-execução do opt-out | Médio | Média | Médio |

---

## 5. Medidas de Mitigação e Salvaguardas de Segurança
* **Criptografia de Ponta a Ponta / Repouso:** Criptografia AES-256 para dados armazenados e TLS 1.3 para dados em trânsito.
* **Minimização de Dados:** Apenas os dados imprescindíveis exigidos por cada Data Broker são solicitados ao titular.
* **Política de Retenção e Exclusão Certa:** Exclusão automática de dados cadastrais após a confirmação do opt-out junto às corretoras ou mediante solicitação do titular via `/lgpd_report`.
* **Controle de Acesso estrito (RBAC):** Restrição de acesso aos ambientes de servidor e chaves de criptografia.
* **Logs de Auditoria Sanitizados:** Logs não contêm PII (informações pessoalmente identificáveis) em texto simples.

---

## 6. Parecer do Encarregado (DPO) e Aprovação
O tratamento de dados realizado pelo **Data Broker Opt-Out Bot** atende aos princípios previstos no Artigo 6º da LGPD (finalidade, adequação, necessidade, livre acesso, qualidade dos dados, transparência, segurança, prevenção, não discriminação e responsabilização). As medidas de segurança implementadas minimizam satisfatoriamente os riscos identificados.

* **Status da Avaliação:** ✅ **APROVADO COM RECOMENDAÇÕES**
* **Assinatura do DPO:** Encarregado de Proteção de Dados
* **Data:** [Data de Aprovação]
