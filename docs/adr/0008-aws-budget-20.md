# Alarme de custo AWS a US$ 20/mês

Depois do Free Plan, a conta será paga. O Terraform cria um AWS Budget de US$ 20/mês com alerta em 80% (US$ 16) no e-mail do operador. O budget não desliga a VM; só evita surpresa. US$ 10 ficaria abaixo do preço da `t4g.small` e alarmaria em falso; US$ 50 não é teto baixo.
