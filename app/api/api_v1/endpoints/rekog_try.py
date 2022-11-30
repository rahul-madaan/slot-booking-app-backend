import os

import boto3


def compare_faces(sourceFile, targetFile):
    client = boto3.client('rekognition')

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    response = client.compare_faces(SimilarityThreshold=80,
                                    SourceImage={'Bytes': imageSource.read()},
                                    TargetImage={'Bytes': imageTarget.read()})

    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at ' +
              str(position['Left']) + ' ' +
              str(position['Top']) +
              ' matches with ' + similarity + '% confidence')

    imageSource.close()
    imageTarget.close()
    return len(response['FaceMatches'])


def main():
    #source = from s3
    # target= upload
    dir_list = os.listdir("/Users/rahul.madan/PycharmProjects/slot-booking-app-backend/stored_faces")
    print(dir_list)

    for pic in dir_list:

        source_file = '/Users/rahul.madan/PycharmProjects/slot-booking-app-backend/stored_faces/' + str(pic)
        target_file = '/Users/rahul.madan/PycharmProjects/slot-booking-app-backend/input_image.jpeg'
        face_matches = compare_faces(source_file, target_file)
        if face_matches == 1:
            print(pic.split(".")[0])
            break
        print("Face matches: " + str(face_matches))



if __name__ == "__main__":
    main()