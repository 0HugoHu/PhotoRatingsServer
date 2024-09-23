from flask import Flask, jsonify, request, send_file
from schedulers import *
from waitress import serve

app = Flask(__name__)


@app.route('/get_unrated_images', methods=['GET'])
def get_unrated_images():
    start_time = time.time()
    log_operation("Starting to load unrated images.")
    unrated_images = []
    largest_folder = max([int(f) for f in os.listdir(UNRATED_FOLDER) if os.path.isdir(os.path.join(UNRATED_FOLDER, f))], default=0)

    for i in range(largest_folder, 0, -1):
        partition_folder = os.path.join(UNRATED_FOLDER, str(i))
        
        if os.path.isdir(partition_folder):
            unrated_images.extend({
                "partition": str(i),
                "filename": filename
            } for filename in os.listdir(partition_folder) if filename.lower().endswith(('.png', '.jpg', '.jpeg')))
        
        if len(unrated_images) >= 10:
            break
    
    unrated_images = unrated_images[:10]
    log_operation(f"Sent {len(unrated_images)} unrated images list from {UNRATED_FOLDER}")
    log_operation(f"Time taken to load images: {time.time() - start_time:.2f} seconds.")
    return jsonify(unrated_images)


@app.route('/images/<partition>/<filename>', methods=['GET'])
def serve_image(partition, filename):
    start_time = time.time()
    log_operation(f"Starting to serve image {partition}/{filename}.")
    image_path = os.path.join(UNRATED_FOLDER, partition, filename)

    if os.path.exists(image_path):
        if os.path.getsize(image_path) > MAX_FILE_SIZE_BYTES:
            compressed_image = compress_image(image_path)
            log_operation(f"Compressed image: {filename} from {image_path}, Time taken: {time.time() - start_time:.2f} seconds.")
            return send_file(compressed_image, mimetype='image/jpeg')

        log_operation(f"Original image: {filename} from {image_path}, Time taken: {time.time() - start_time:.2f} seconds.")
        return send_file(image_path)

    log_operation(f"Image not fod: {filename} in partition {partition}")
    return "Image not fod", 404


@app.route('/rate_image', methods=['POST'])
async def rate_image():
    start_time = time.time()
    log_operation("Starting to rate an image.")
    data = request.get_json()
    image_name = data.get('image_name')
    rating = data.get('rating')
    partition = data.get('partition')

    if image_name and rating:
        source_path = os.path.join(UNRATED_FOLDER, partition, image_name)
        destination_folder = os.path.join(RATED_FOLDER, str(rating))

        os.makedirs(destination_folder, exist_ok=True)
        destination_path = os.path.join(destination_folder, image_name)
        
        shutil.move(source_path, destination_path)
        image_id = get_image_identifier(destination_path)
        update_log(image_id, 'rated')

        log_operation(f"Moved rated image: {image_name} from {source_path} to {destination_path}")

        if not os.listdir(os.path.join(UNRATED_FOLDER, partition)):
            os.rmdir(os.path.join(UNRATED_FOLDER, partition))
            log_operation(f"Deleted empty partition folder: {partition}")

        log_operation(f"Time taken to rate image: {time.time() - start_time:.2f} seconds")
        return jsonify({"status": "success", "message": f"Image {image_name} moved to rated {rating} folder"}), 200

    log_operation("Invalid data received for rating an image.")
    return jsonify({"status": "error", "message": "Invalid data"}), 400


if __name__ == '__main__':
    start_scheduler()
    serve(app, host='0.0.0.0', port=5410)
