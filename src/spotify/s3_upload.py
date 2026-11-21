
import boto3
from pathlib import Path

AWS_PROFILE = "fellipe-oliveira"
AWS_REGION = "us-east-2"
S3_BUCKET = "spotify-data-engineering-334116998170-us-east-2"


def upload_to_s3(s3_client, local_file, s3_key):
    """
    Envia um arquivo local para o AWS S3.
    """

    local_path = Path(local_file)

    if not local_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {local_file}")

    s3_client.upload_file(
        str(local_path),
        S3_BUCKET,
        s3_key
    )

    print(f"Upload concluído: {s3_key}")


def upload_directory(s3_client, local_dir, s3_prefix):
    """
    Envia todos os arquivos de um diretório para o S3,
    preservando a estrutura de subdiretórios.
    """

    directory = Path(local_dir)

    if not directory.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {local_dir}")

    files = [file for file in directory.rglob("*") if file.is_file()]

    for file in files:
        relative_path = file.relative_to(directory).as_posix()
        s3_key = f"{s3_prefix.rstrip('/')}/{relative_path}"

        upload_to_s3(s3_client, file, s3_key)

    print(f"\nTotal de arquivos enviados para {s3_prefix}/: {len(files)}")


if __name__ == "__main__":

    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=AWS_REGION
    )

    s3_client = session.client("s3")

    print("Iniciando upload para AWS S3...\n")

    # Bronze: arquivos JSON
    upload_directory(
        s3_client,
        local_dir="data/bronze",
        s3_prefix="bronze"
    )

    # Silver: arquivos CSV
    upload_directory(
        s3_client,
        local_dir="data/processed",
        s3_prefix="silver"
    )

    print("\nProcesso finalizado!")


# if __name__ == "__main__":
#     upload_to_s3(
#         local_file="data/bronze/artists/artists.json",
#         s3_key="bronze/artists/artists.json"
#     )
