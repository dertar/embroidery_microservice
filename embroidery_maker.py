import cv2
import numpy as np
import math
import random
import options
import database
import webcolors

class EmbroideryMaker():
    def __init__(self, colors_db, symbols_db):
        self.colors_db = colors_db
        self.symbols_db = symbols_db

    def distance_color(self, rgbA, rgbB):
        return math.sqrt(math.pow(rgbA[0] - rgbB[0], 2) + math.pow(rgbA[1] - rgbB[1], 2) + math.pow(rgbA[2] - rgbB[2], 2))

    def gen_embroidery(self, img, embroidery_dimension_size, dimension_size, xo, k):
        aspect_ratio = (int(dimension_size[0] / embroidery_dimension_size[0]), int(dimension_size[1] / embroidery_dimension_size[1]))
        resized_img = cv2.resize (img, embroidery_dimension_size)
        resized_date = np.float32(resized_img.reshape((-1, 3)))

        criteria = (cv2.TERM_CRITERIA_EPS, 30, 1.0)
        ret, labels, centers = cv2.kmeans(resized_date, k, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)
        res = centers[labels.flatten()]

        unique_colors = self.get_unique_colors(res.tolist())
        similar_colors = self.get_similar_colors(unique_colors)
        # print(similar_colors)
        embroidery_img = np.empty([len(res), 3], dtype=np.uint8)

        for i, val in enumerate(res):
            for similar in similar_colors:
                if np.array_equal(val, similar[0]):
                    embroidery_img[i] = similar[1]


        embroidery_img = embroidery_img.reshape((resized_img.shape))

        tmp = cv2.resize (embroidery_img, dimension_size, interpolation=cv2.INTER_NEAREST)


        data_color = {}

        for color in similar_colors:
            data_color[color[3].lower()] = (color[2], color[4])

        # print(data_color)
        if True:
            self.draw_symbols(tmp, embroidery_img, aspect_ratio, data_color)

        if xo[0]:
            self.draw_xo_coordinates(tmp, xo[1], aspect_ratio)
        return tmp
        #
        # cv2.imshow("s1",tmp)
        #
        # cv2.waitKey(0)
        # cv2.destroyWindow()

    def draw_symbols(self, img, embroidery_img, aspect_ratio, data_color):
        # print(every)
        width, height = len(img[0]), len(img)
        # count_x_symbols, count_y_symbols = int(width / every[0]), int(height / every[1])
        scaleFont = 0.5
        thickness = 1

        for y in range(0, len(embroidery_img[0])):
            for x in range(0, len(embroidery_img)):
                hex_color = webcolors.rgb_to_hex(embroidery_img[x][y]).lower();

                try:
                    ch = data_color[hex_color][1]
                except KeyError:
                    ch = '?'

                size = cv2.getTextSize(ch, cv2.FONT_HERSHEY_PLAIN, scaleFont, thickness)

                x_pos =  y * aspect_ratio[0] + int(size[0][0] / 2)
                y_pos =  x * aspect_ratio[1] + int(size[0][1] / 2) + int(aspect_ratio[1] / 2)

                cv2.putText(img, ch, (x_pos, y_pos), cv2.FONT_HERSHEY_PLAIN, scaleFont, 127)

    def draw_xo_coordinates(self, img, every, aspect_ratio):
        width, height = len(img[0]), len(img)
        every_in_pixels = (every[0] * aspect_ratio[0], every[1] * aspect_ratio[1])
        count_x_lines, count_y_lines = int(width / every_in_pixels[0]), int(height / every_in_pixels[1])

        for x in range(1, count_x_lines):
            coord_x = int(x * every_in_pixels[0])
            cv2.line(img, (coord_x, 0), (coord_x, height), (0,0,0))

        for y in range(1, count_y_lines):
            coord_y = int(y * every_in_pixels[1])
            cv2.line(img, (0, coord_y), (width, coord_y), (0,0,0))

    def get_unique_colors(self, color_lst):
        unique_colors = []

        for c in color_lst:
            if unique_colors.count(c) == 0:
                unique_colors.append(c)
        return unique_colors

    def get_similar_colors(self, unique_colors):
        similar_colors = []
        distance_colors = []

        for c in unique_colors:
            distance_colors.append(self.find_similar_color_from_db(c))

        symbols = random.sample(self.symbols_db, len(unique_colors))

        for unique_color, similar, ch in zip(unique_colors, distance_colors, symbols):
            color_with_minimum_distance = min(similar, key=similar.get)
            color = np.array(unique_color)

            replace_color = np.array(self.colors_db[color_with_minimum_distance][1])

            similar_colors.append ((color, replace_color, self.colors_db[color_with_minimum_distance][0][1], self.colors_db[color_with_minimum_distance][0][4] ,ch[0]))

        # todo: sure if similar colors has not duplicate

        return similar_colors

    def find_similar_color_from_db(self,color):
        ret = {}
        for index, c in enumerate(self.colors_db):
            ret[index] = self.distance_color(c[1], color)
        return ret

def get_img_size(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return (len(img[0]), len(img))

# data = database.load_data_from_db(options.DB_PATH)
#
# maker = EmbroideryMaker(data[0], data[1])
# maker.gen_embroidery(cv2.imread('D:\\Downloads\\sj.jpg', cv2.IMREAD_COLOR), (80, 80), (800,800), (True, (5, 5)), 24)
