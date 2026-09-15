# PostgreSQL de produção no Compose, não RDS

O banco de produção continua sendo o serviço `db` do `docker-compose.prod.yml`, no volume da mesma EC2 `t4g.small`. RDS foi recusado: no Free Plan desta conta não há cota mensal grátis de RDS, e depois dos créditos seria uma segunda conta recorrente. Backup e retenção ficam no desenho da issue #33 (artefato criptografado fora da VM), não num banco gerenciado.
