from datetime import date

# Solicita a data de nascimento do usuário
ano_nascimento = int(input("Digite o ano de nascimento: "))
mes_nascimento = int(input("Digite o mês de nascimento: "))
dia_nascimento = int(input("Digite o dia de nascimento: "))

# Obtém a data de hoje
hoje = date.today()

# Calcula a idade inicial (subtraindo os anos)
idade = hoje.year - ano_nascimento

# Verifica se o aniversário já passou este ano
if (mes_nascimento, dia_nascimento) > (hoje.month, hoje.day):
    idade -= 1

print(f"A idade é: {idade}")