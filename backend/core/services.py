from imagekitio import ImageKit
from base64 import b64encode
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()


class ImageKitService:
    def __init__(self):
        self.ik = ImageKit(
            private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
            public_key=os.getenv('IMAGEKIT_PUBLIC_KEY'),
            url_endpoint=os.getenv('IMAGEKIT_URL_ENDPOINT')
        )

    def create_profile_image(self, image_file, user):
        """Cria uma nova imagem de perfil no ImageKit"""
        return self.upload_profile_image(image_file, user)

    def upload_profile_image(self, image_file, user):
        """Faz upload de uma nova imagem de perfil"""
        nome_arquivo = f"foto_perfil_{user.usuario}.jpg"
        imagem_base64 = b64encode(image_file.read())

        return self.ik.upload_file(
            file=imagem_base64,
            file_name=nome_arquivo,
            options=UploadFileRequestOptions(
                use_unique_file_name=False,
                overwrite_file=True
            )
        )

    def delete_image(self, file_id: str):
        """Deleta uma imagem do ImageKit"""
        if file_id:
            return self.ik.delete_file(file_id=file_id)
        return None


imagekit_service = ImageKitService()
