# from bluebird.settings import  CLOUDINARY_NAME,CLOUDINARY_API_KEY,CLOUDINARY_API_SECRET
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api

# cloudinary.config(
# cloud_name=CLOUDINARY_NAME,
# api_key=CLOUDINARY_API_KEY,
# api_secret=CLOUDINARY_API_SECRET
# )

# def cloudinary_upload_media(image,imageDir):
#     image_data=cloudinary.uploader.upload(image, folder=imageDir)
#     return (image_data['url'],image_data['public_id'])

# def delete_cloudinary_media(public_id):
#     cloudinary.uploader.destroy(public_id)