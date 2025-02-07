# Import statement untuk modul dan pustaka yang diperlukan
import itertools  # Mengimpor pustaka untuk alat iterasi
import kivy  # Mengimpor pustaka Kivy untuk antarmuka pengguna grafis (GUI)
# Mengimpor properti tertentu dari Kivy
from kivy.properties import ListProperty, OptionProperty
import os  # Mengimpor modul OS untuk interaksi dengan sistem operasi
import sys  # Mengimpor modul sys untuk fungsi dan variabel spesifik sistem
# Mengimpor fungsi resource_add_path dari sumber daya Kivy
from kivy.resources import resource_add_path
# Mengimpor kelas BoxLayout dari modul Kivy UIX
from kivy.uix.boxlayout import BoxLayout
# Mengimpor kelas GridLayout dari modul Kivy UIX
from kivy.uix.gridlayout import GridLayout
# Mengimpor kelas MatrixValue dari modul kustom uixwidgets
from uixwidgets import MatrixValue
from kivy.utils import platform  # Mengimpor fungsi platform dari utilitas Kivy
from kivy.app import App  # Mengimpor kelas App dari modul aplikasi Kivy
from kivy.config import Config  # Mengimpor kelas Config dari modul konfigurasi Kivy
# Mengimpor kelas Window dari modul jendela inti Kivy
from kivy.core.window import Window
import re  # Mengimpor modul re untuk ekspresi reguler
from fractions import Fraction  # Mengimpor kelas Fraction dari modul fractions

# Spesifikasi versi Kivy yang dibutuhkan
kivy.require('2.0.0')

# // Cari sumber daya dalam file root proyek (opsional)
Config.write()
kivy.resources.resource_add_path("./")

# Fungsi untuk mengatur warna status bar menjadi putih pada Android (dengan catatan masalah potensial pada ROM yang dimodifikasi)


def white_status_bar():
    # Impor modul Android yang diperlukan
    from android.runnable import run_on_ui_thread  # type: ignore

    @run_on_ui_thread
    def _white_status_bar():
        # Impor kelas yang diperlukan dari SDK Android
        from jnius import autoclass
        WindowManager = autoclass('android.view.WindowManager$LayoutParams')
        Color = autoclass('android.graphics.Color')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        window = activity.getWindow()
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.WHITE)
    _white_status_bar()

# Definisi kelas untuk grid layout yang berisi semua unit matriks


class MatrixGrid(GridLayout, BoxLayout):
    # Inisialisasi order sebagai ListProperty dengan nilai default [3, 3]
    order = ListProperty([3, 3])

    # Fungsi untuk membuat tampilan Matriks berdasarkan order yang diberikan
    def on_order(self, *args):
        app.error_list = []  # Inisialisasi error_list di aplikasi

        self.clear_widgets()  # Hapus widget yang sudah ada dalam layout
        # Tetapkan jumlah baris dalam layout berdasarkan order[0]
        self.rows = int(self.order[0])
        # Tetapkan jumlah kolom dalam layout berdasarkan order[1]
        self.cols = int(self.order[1])

        # Buat widget input teks untuk setiap unit matriks berdasarkan order
        for i in range(1, self.order[0] + 1):
            for k in range(1, self.order[1] + 1):
                text_input = MatrixValue()  # Buat instansi kelas MatrixValue
                # Tambahkan widget input teks ke dalam layout
                self.add_widget(text_input)

    # Fungsi untuk menampilkan matriks dalam layout MatrixGrid
    def show_matrix(self, matrix):
        # Tetapkan order berdasarkan dimensi matriks
        self.order = [len(matrix), len(matrix[0])]
        unpacked_matrix = list(itertools.chain(*matrix))  # Flatten matriks
        unpacked_matrix.reverse()  # Balik matriks yang sudah diflatten

        # Tampilkan nilai-nilai matriks dalam widget input teks yang sesuai
        for k in range(0, len(unpacked_matrix)):
            # Tetapkan widget input teks sebagai hanya baca
            self.children[k].readonly = True
            # Tetapkan nilai teks dalam widget
            self.children[k].text = str(unpacked_matrix[k])

    # Metode konstruktor untuk MatrixGrid
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Panggil fungsi on_order untuk menginisialisasi layout berdasarkan order default
        self.on_order()

# // Aplikasi Utama
# // Semua inisiasi, proses bakalan dilakuin di sini


class MatrixCalculator(App):
    # Config_format === Operation_Type: (Input_type, Order_type, Output_type)
    operation_config = {
        'Tambah': ('double', 'same', 'matrix'),
        'Kurang': ('double', 'same', 'matrix'),
        'Determinan': ('single', 'square', 'number'),
        'Rank': ('single', 'any', 'number'),
        'Dot Produk': ('double', 'chain', 'matrix'),
        'Invers': ('single', 'square', 'matrix')}
    operation_mode = OptionProperty(
        'Determinan', options=operation_config.keys())
    error_list = ListProperty([])
    operation_type = OptionProperty('single', options=['single', 'double'])

    def __init__(self, **kwargs):
        self.title = "Matrix Calculator ITK"
        global app
        app = self
        super().__init__(**kwargs)

    def on_operation_mode(self, *args):
        self.root.ids.display_box.text = ""

    def on_error_list(self, obj, value):
        temp = list(value)
        temp = list(set(self.error_list))  # Removes same error multiple times
        temp = list(filter(None, temp))  # Removes Empty(None) values if any
        self.error_list = list(temp)

        length = len(temp)
        if length == 0:
            error_string = ""
        elif length < 4:
            error_string = '\n'.join(self.error_list[:4])
        else:
            error_string = '\n'.join(self.error_list[:3]) + "\n ..."

        self.root.ids.display_box.text = error_string

    # Convert input_matrix into nested lists
    def make_matrix(self, matrix):

        # // Receives all text boxes of Matrix Grid
        children_list = matrix.children
        if not children_list:  # // Checks that calculation not done on empty set of values
            return "---"

        error_observed = False
        self.error_list = []

        for child in children_list:  # // Checks and Fetches all units of matrix one-by-one
            error = Validator().chk_value(child.text)

            if error:
                error_observed = True
                self.error_list.append(error)

        if error_observed:
            return "---"
        else:
            self.error_list = []
            values_list = [Fraction(child.text).limit_denominator(999)
                           for child in children_list]

        # // Covert Linear List to Matrix-type Nested List
        values_list.reverse()
        Mvalues_list = []
        temp_list = []
        order = matrix.order

        for i in range(order[0]):
            for k in range(order[1]):
                temp_list.append(values_list[order[1] * i + k])
            Mvalues_list.append(list(temp_list))
            temp_list.clear()

        return Mvalues_list

    # ////// Receive values of matrix units provided in grid layout
    def calculate(self):

        order_type = self.operation_config[self.operation_mode][1]
        improper_order = Validator().chk_order(
            [self.root.ids.input_matrix_1.order, self.root.ids.input_matrix_2.order], order_type)
        if improper_order:
            return

        matrices_list = [self.make_matrix(self.root.ids.input_matrix_1)]
        if self.operation_config[self.operation_mode][0] == 'double':
            matrices_list.append(self.make_matrix(
                self.root.ids.input_matrix_2))

        if "---" in matrices_list:
            return

        answer_string = ""
        WHITE_SPACE = "     "

        if self.operation_mode == "Determinan":
            determinant = Calculator().determinant(matrices_list[0])
            answer_string += f"Determinan:{WHITE_SPACE}[anchor='right']{determinant}"

        elif self.operation_mode == "Tambah":
            sum = Calculator().add(matrices_list[0], matrices_list[1])
            answer_string += f"Tambah:{WHITE_SPACE}"
            self.root.ids.output_matrix.show_matrix(sum)
            self.root.ids.ans_button.trigger_action()
            # transpose = Calculator().transpose(sum)
            # self.root.ids.transpose_button.show_matrix(transpose)
            # self.root.ids.transpose_matrix.show_matrix(transpose)
            # self.root.ids.transpose_button.trigger_action(transpose)v
        elif self.operation_mode == "Kurang":
            subtract = Calculator().subtract(
                matrices_list[0], matrices_list[1])
            answer_string += f"Kurang:{WHITE_SPACE}"
            self.root.ids.output_matrix.show_matrix(subtract)
            self.root.ids.ans_button.trigger_action()

        elif self.operation_mode == "Rank":
            rank = Calculator().rank_of_matrix(matrices_list[0])
            answer_string += f"Rank:{WHITE_SPACE}{rank}"

        elif self.operation_mode == "Dot":
            product = Calculator().product(matrices_list[0], matrices_list[1])
            answer_string += f"Dot Produk:{WHITE_SPACE}"
            self.root.ids.output_matrix.show_matrix(product)
            self.root.ids.ans_button.trigger_action()

        elif self.operation_mode == "Invers":
            determinant = Calculator().determinant(matrices_list[0])
            if determinant == 0:
                self.root.ids.display_box.text = ""
                answer_string += "[size=19sp]Inverse tidak dapat dilakukan\njika determinan 0.[/size]"
            else:
                inverse = Calculator().inverse(matrices_list[0])
                answer_string += f"Inverse:{WHITE_SPACE}"
                self.root.ids.output_matrix.show_matrix(inverse)
                self.root.ids.ans_button.trigger_action()

        else:
            answer_string += "Pilih operasi dan kalkulasi ulang"

        # // Sets the answer to display_box
        self.root.ids.display_box.text = f"[size=20sp]{answer_string}[/size]"

    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        if platform == "android":
            # // Added to fix text-box hidden behind keyboard
            Window.softinput_mode = 'below_target'
            white_status_bar()
        else:
            Window.size = (450, 800)  # // Default size for desktop

        return MainWindow()


# Root layout of our app
class MainWindow(BoxLayout):
    pass


class Calculator:

    def sub_matrix(self, A, order):
        minors = []
        for i in range(len(A) - order + 1):
            partial_minor = A[i: i + order]
            for k in range(len(A[1]) - order + 1):
                minor = [B[k: k + order] for B in partial_minor]
                minors.append(minor)
        return minors

    def transpose(self, A):
        transposed_matrix = [[k[t] for k in A] for t in range(len(A[0]))]
        print(transposed_matrix)
        return transposed_matrix

    def determinant(self, A, total=0):
        # Section 1: store indices in list for row referencing

        indices = list(range(len(A)))

        # Section 2: when at 2x2 sub-matrices recursive calls end
        if len(A) == 2 and len(A[0]) == 2:
            val = A[0][0] * A[1][1] - A[1][0] * A[0][1]
            return val

        # Section 3: define sub-matrix for focus column and
        #      call this function
        for fc in indices:  # A) for each focus column, ...
            # find the sub-matrix ...
            As = list(A)  # B) make a copy, and ...
            As = As[1:]  # ... C) remove the first row
            height = len(As)  # D)

            for i in range(height):
                # E) for each remaining row of submatrix ...
                #     remove the focus column elements
                As[i] = As[i][0:fc] + As[i][fc + 1:]

            sign = (-1) ** (fc % 2)  # F)
            # G) pass sub-matrix recursively
            sub_det = Calculator().determinant(As)
            # H) total all returns from recursion
            total += sign * A[0][fc] * sub_det

        return total

    def inverse(self, A):
        A_copy = list(A)
        det_A = self.determinant(A)
        inversed_matrix = []
        for i in range(len(A)):
            A_copy.pop(i)
            inversed_matrix.append([])
            for j in range(len(A[1])):
                minor_matrix = [k[:j] + k[j + 1:] for k in A_copy]
                cofactor = ((-1) ** (i + j)) * \
                    self.determinant(minor_matrix) / det_A
                inversed_matrix[i].append(cofactor)
                print(f"Kofaktor = {cofactor} untuk {minor_matrix}")
            else:
                A_copy = list(A)
        else:
            inversed_matrix = self.transpose(inversed_matrix)

        return inversed_matrix

    def rank_of_matrix(self, A):
        max_rank = min(len(A), len(A[1]))
        print("**** Rank detection started ****")
        for k in reversed(range(1, max_rank + 1)):
            print("on order:", k)
            for f in self.sub_matrix(A, k):
                print("Checking for", f)
                det = self.determinant(f)
                print("Got Determinant:", det)
                if det != 0:
                    print("!! Accepted Rank:", k)
                    return k
        else:
            return 1

    def add(self, A, B):
        summed_matrix = [list(zip(m, n))for m, n in zip(A, B)]
        for j in range(0, len(summed_matrix)):
            for k in range(0, len(summed_matrix[j])):
                pair = summed_matrix[j][k]
                summed_matrix[j][k] = pair[0] + pair[1]
        print(summed_matrix)
        return summed_matrix

    def subtract(self, A, B):
        reduce_matrix = [list(zip(m, n))for m, n in zip(A, B)]
        for r in range(0, len(reduce_matrix)):
            for k in range(0, len(reduce_matrix[r])):
                pair = reduce_matrix[r][k]
                reduce_matrix[r][k] = pair[0] - pair[1]
        print(reduce_matrix)
        return reduce_matrix

    def product(self, A, B):
        group_by_column = [[k[t] for k in B] for t in range(len(B[0]))]
        print("Grouped by column =", group_by_column)
        product_matrix = []

        for j in A:
            row_matrix = []
            print("=============")

            for k in group_by_column:
                print("=============")
                print(j, '*', k)
                term = [m * n for m, n in zip(j, k)]
                row_matrix.append(sum(term))
                print("Answer =", sum(term))

            else:
                product_matrix.append(row_matrix)

        print("******************************")
        print("Final Product Matrix =", product_matrix)
        return product_matrix


"""
    B = [[3, 4, 5, 9], [1, -4, 5, 2], [-2, 8, 4, 4]]
    A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    product(A, B)
"""
"""
    A = [[Fraction(1), Fraction(2), Fraction(3), Fraction(-2)],
        [Fraction(4), Fraction(1, 3), Fraction(5), Fraction(6)],
        [Fraction(7), Fraction(9), Fraction(-3, 7), Fraction(8)],
        [Fraction(7), Fraction(3), Fraction(-1), Fraction(8, 3)]]
    inverse(A)
"""


class Validator:
    """Class dedicated to verify user inputs
    """

    def chk_value(self, value):
        """Checks for standard pattern. If False, then do some pre-tests to find exact problem.

        Args:
            value (Fraction): Fractional value entered in matrix

        Returns:
            String: Error statement if error found, otherwise None
        """
        value = re.sub(r"\s", "", value)  # // Removes all types of whitespaces
        error = None

        master_pattern = re.compile(
            r"^((\+|\-)?\d{1,3}(([\.]\d{1,2})|([\/]\d{1,3}))?){1}$")

        if not re.match(master_pattern, value):
            if value == '':
                error = "! Any part of matrix can't be EMPTY."
            elif re.search(r"[^\+\-\.\/0-9]", value):
                error = "! Invalid characters in one/more values."
            elif len(re.findall(r"[\/]", value)) > 1:
                error = "! Multiple \'/\' in single value not allowed."
            elif re.search(r"[\/](\+|\-)", value):
                error = "! +/- can be in Numerator, NOT in Denominator."
            elif re.match(r"^((\+|\-)?\d{1,3}([\.]\d)?[\/](\+|\-)?\d{1,3}([\.]\d)?)$", value):
                error = "! Decimal and Fraction can't be together."
            elif re.search(r"\d{4,}", value):
                error = "! Max. 3 digits allowed for numerical part."
            else:
                error = "! Improper structure of entered value/s."

        return error

    def chk_order(self, orders, order_type):
        error = ""

        if order_type == 'square':
            if orders[0][0] != orders[0][1]:
                error = "! Square matrix required for " + app.operation_mode
        elif order_type == 'same':
            if orders[0] != orders[1]:
                error = "! Order of both matrices should be same."
        elif order_type == 'chain':
            if orders[0][1] != orders[1][0]:
                error = "! Columns of M1 should equals to rows of M2"

        if error:
            app.error_list = [error]

        return error


# /// Driver needed to self start the app ---- VROOM! VROOM!
if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MatrixCalculator().run()
