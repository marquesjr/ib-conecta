# LocalStack só para S3, com atalho .bat no Windows

No desenvolvimento, LocalStack Community emula apenas o bucket S3 de backups (`localhost:4566`). Um script `.bat` sobe o LocalStack, garante o bucket e o Compose local (`docker-compose.yml`). Terraform de produção continua na AWS real (`us-east-2`). Emular EC2/VPC/Elastic IP no LocalStack fica de fora por enquanto.
