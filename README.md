1. Clínica Médica Bot:
Chatbot para cadastro de pacientes, atendimento e agendamento automático integrado ao Google Calendar

Projeto desenvolvido em Python com foco em automação de processos, coleta de dados e integração com APIs, simulando um fluxo real de operação de clínicas médicas.

2. Visão Geral:
Clínicas médicas gastam muito tempo com tarefas manuais como:
  * Coleta de dados de pacientes
  * Organização da agenda
  * Confirmação de horários disponíveis
  * Comunicação com o médico
Este projeto automatiza todo esse fluxo através de um chatbot.

O sistema coleta dados, armazena, processa e agenda consultas automaticamente — funcionando como uma assistente virtual.

3. Principais Funcionalidades:
  3.1. Cadastro completo de pacientes via chat
   Coleta automática de:
     * Nome completo
     * CPF
     * Data de nascimento
     * Gênero
     * Telefone
     * Doenças
     * Medicamentos
     * Alergias
  Todos os dados são validados e armazenados.

 3.2 Agendamento inteligente:
   O sistema:
   * Consulta a agenda do Google Calendar
   * Analisa horários livres automaticamente
   * Sugere horários ao paciente
   * Cria o evento automaticamente na agenda do médico
  Tudo sem intervenção humana.

3.3 Automação diária da agenda médica:
  Um job automático roda todos os dias:
    * Consulta os compromissos do dia
    * Envia a agenda completa para o médico via Telegram
  Utilizando APScheduler para automação.

4. Conceitos aplicados no projeto:
  * Data ingestion via chatbot
  * Validação e transformação de dados
  * Persistência de dados (SQLite)
  * Integração com API externa (Google Calendar)
  * Automação com jobs agendados
  * Processamento de intervalos de tempo e disponibilidade
  * Organização em arquitetura modular

5. Arquitetura do Projeto:
Fluxo simplificado:
Paciente → Chatbot → Validação → Banco SQLite
                              ↓
                    Google Calendar API
                              ↓
               Agendamento automático
                              ↓
                 Notificação diária médico

6. Tecnologias Utilizadas:
   * Python
   * python-telegram-bot
   * SQLite
   * Google Calendar API
   * Job queue
   * python-dotenv

7. Variáveis de Ambiente
  * O projeto utiliza .env para segurança.
  * Crie um arquivo .env baseado em .env.example.
Exemplo:

TELEGRAM_TOKEN=
CHAT_ID_MEDICO=
GOOGLE_CREDENTIALS_FILE=
CALENDAR_ID=

  7.1 Como Executar Localmente:
    1. Criar ambiente virtual:
    2. python -m venv venv
    3. Instalar dependências:
      pip install -r requirements.txt
    4. Configurar variáveis de ambiente
    5. Criar .env baseado no .env.example
    6. Executar o bot
      python -m bot.main

8. Status do Projeto:
  * Funcional via Telegram
  * Migração para WhatsApp em andamento
  * Planejado deploy em cloud

9. Próximos Passos:
  * Integração com WhatsApp API
  * Deploy em ambiente cloud
  * Migração para banco em nuvem
  * Dashboard para clínicas
