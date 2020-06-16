#Nguyễn Hoàng Thịnh - 17110372

from tkinter import Frame, Tk, Label, Button, Entry, PhotoImage, Listbox
from PIL import ImageTk, Image
import os
from min_conflict import *

#Class này kế thừa từ Frame, sẽ đại diện cho 1 cửa sổ của chương trình
class App(Frame):

	def __init__(self,parent):
		Frame.__init__(self,parent)
		self.parent = parent
		self.tileList = []
		self.currentNumOfQueens = None
		self.initUI()


	# Hàm này có nhiệm vụ khởi tạo các widget chứa bên trong App
	def initUI(self):

		# Cấu hình layout cho cửa sổ này
		# Tham số side = "left" cho biết layout sẽ cố định bên trái, fill = "both" thì kích thước của layout
		# sẽ lắp đầy 2 bên, expand = True cho phép mở rộng
		self.pack(side = "left", fill = "both", expand = True)

		# Tạo một frame, frame này sẽ chứa MAP đặt n Queens
		# Tham số self cho biết widget sẽ chứa nó, width là chiều rộng, height là chiều cao
		self.map = Frame(self, width = 600, height = 600)
		self.map.pack(side = "left", fill ="both", expand = True)

		# Lấy ra thông tin chiều dài và rộng tính theo pixel của MAP, ta trừ đi kích thước 20 
		# để cách đều ra 2 bên
		self.map.update()
		self.x = int(self.map.winfo_width() - 20)
		self.y = int(self.map.winfo_width() - 20)

		# Tạo frame thứ 2, frame này sẽ chưa textbox cho ta nhập số n queens, số lần lặp của thuật toán
		self.frameWidget = Frame(self,width = 150)
		self.frameWidget.pack(side = "left", fill ="both", expand = True)


		self.lbNumOfQueens = Label(self.frameWidget, text = "Num of Queens")

		# Tham số pady = 25, để label cách đều về 2 phía theo trục y 25 px
		self.lbNumOfQueens.pack(pady = 25)

		# Tạo textbox để nhập số quân hậu cần đặt

		self.entryNumOfQueens = Entry(self.frameWidget)
		self.entryNumOfQueens.pack()

		# Tạo button để chạy giải quyết thuậ toán
		# Tham số command = self.resolving để tạo sự kiện khi nhấn button này
		self.btnResolving = Button(self.frameWidget, text = "Min-conflict algorithm", command = self.resolving)
		self.btnResolving.pack(pady = 50)

		# Tạo label để hiển thị thời gian chạy của thuật toán
		self.lbTime= Label(self.frameWidget, text = "0.00s")

		# Tham số pady = 25, để label cách đều về 2 phía theo trục y 25 px
		self.lbTime.pack(pady = 25)


	# Hàm tạo bàn cờ numOfQueens x numOfQueens
	def createMap(self,numOfQueens):
		for widget in self.map.winfo_children():
			widget.destroy()

		self.map.update()

		self.tileList.clear()

		# Ta lấy chiều dài và rộng của 1 ô theo pixel
		w = int(self.x/numOfQueens)
		h = int(self.y/numOfQueens)

		# Cấu hình cột hàng cho MAP
		for k in range(numOfQueens):
			self.map.columnconfigure(k, pad = 2)
			self.map.rowconfigure(k, pad = 2)

		# Tạo các label đại diện cho một ô trong MAP
		for i in range(numOfQueens):
			self.tileList.append([])
			for j in range(numOfQueens):
				# Tạo một ảnh pixel, để khi ta set width và height cho Label thì nó sẽ lấy theo pixel
				# chứ không phải mm

				#Ta chỉnh các background xen kẽ nhau
				bg = "white"
				if (i+j) % 2 == 0:
					bg = "gray"
				pixelVirtual = PhotoImage(width = 1, height = 1) 
				lb = Label(self.map, image = pixelVirtual, width = w, height = h, bg = bg,padx = 2, pady = 2)
				lb.grid(row = i, column = j) # Đặt nó vào hàng i, cột j của MAP
				self.tileList[i].append(lb)

	'''
	Hàm tìm ra solution và đặt các con hậu lên MAP
	'''
	def resolving(self):
		# Khi thuật toán bắt đầu tìm kiếm, ta tiến hành khóa button này lại, tránh trường hợp
		# click nhiều lần từ người dùng
		self.btnResolving["state"] = "disabled"

		numOfQueens = int(self.entryNumOfQueens.get())

		# Ta kiểm tra xem số hậu được nhập từ người dùng là lần đầu tiên hay là số hậu mới, hay 
		# là chỉ tìm kiếm cách đặt hậu mới
		# self.currentNumOfQueens = None thì ban đầu ta sẽ tạo ra một cái map mới hoặc
		# số hậu nhận từ người dùng ở lần tiếp theo khác với số hậu nhập từ người dùng ở lần trước đó
		# thì ta cũng tạo ra map mới. Ngược lại thì ta không cần tạo map mới mà chỉ cần đặt lại vị trí
		# hình ảnh quân hậu
		if self.currentNumOfQueens == None or self.currentNumOfQueens != numOfQueens:
			self.currentNumOfQueens = numOfQueens
			self.isNewMap = True
		else:
			self.isNewMap = False


		solution, ti = getResults(numOfQueens)

		if self.isNewMap == True:
			self.createMap(numOfQueens)

		self.setTheQueens(numOfQueens,solution)
		self.lbTime.configure(text = str(ti)+"s")

		# Thuật toán chạy xong, các con hậu được đặt, ta mở khóa button cho người dùng tìm kiếm
		# các cách đặt khác
		self.btnResolving["state"] = "active"


	'''
	Hàm đặt các quân hậu dựa vào solution tìm được
	'''
	def setTheQueens(self,numOfQueens,solution):
		for i in range(numOfQueens):
			for j in range(numOfQueens):
				self.tileList[i][j].configure(image = None)
				self.tileList[i][j].image = None

		for column, row in solution.items():
			image =ImageTk.PhotoImage(Image.open(os.getcwd()+"/queen.png"))
			self.tileList[row][column].configure(image = image)
			self.tileList[row][column].image = image





#Tạo một cửa sổ
tk = Tk()

app = App(tk)

#Lệnh gọi hiển cửa sổ
tk.mainloop()


