# HTTPS na VM: Caddy + Elastic IP

TLS de produção é o Caddy do `docker-compose.prod.yml`, com Let’s Encrypt, na EC2 que tem Elastic IP. Security group libera 80/443 para o mundo e SSH só de CIDR conhecido. Application Load Balancer e CloudFront foram recusados nesta fase: o ALB sozinho custa mais que a `t4g.small` e quebra o teto baixo. O DNS canônico (#35) aponta `www.ibsantaleopoldina.com.br` para o Elastic IP.
