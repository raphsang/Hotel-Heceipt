import tkinter as tk
from tkinter import PhotoImage, messagebox
from PIL import Image, ImageTk
from fpdf import FPDF
import os

class HotelSaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The G Star Hotel")

        self.hotel_name = "The G Star Hotel"
        self.hotel_location = "Downtown, Kabarnet"

        self.tax_rate = 0.10
        self.items = []
        self.prices = {
            "Pizza": 100.00,
            "Mixx Full": 100.00,
            "Coffee": 340.00,
            "Sandwich": 150.00,
            "Salad": 200.00
        }

        # Load and resize image for the title (optional)
        self.icon_image = None
        try:
            original_image = Image.open("images/images.png")
            resized_image = original_image.resize((50, 50))  # Resize the image
            self.icon_image = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or resize image: {e}")

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Create a PanedWindow to split the page
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create frames for left and right panels
        self.left_frame = tk.Frame(self.paned_window, width=300, bg='lightgrey')
        self.right_frame = tk.Frame(self.paned_window, width=300, bg='white')

        self.paned_window.add(self.left_frame, stretch='always')
        self.paned_window.add(self.right_frame, stretch='always')

        # Left frame widgets
        self.title_frame = tk.Frame(self.left_frame, bg='lightgrey')
        self.title_frame.pack(padx=10, pady=10, fill=tk.X)

        # Add image and title
        if self.icon_image:
            self.icon_label = tk.Label(self.title_frame, image=self.icon_image, bg='lightgrey')
            self.icon_label.pack(side=tk.TOP, pady=(0, 5))  # Add padding below the icon

        tk.Label(self.title_frame, text=self.hotel_name, font=("Arial", 24, "bold"), bg='lightgrey').pack(side=tk.TOP)

        tk.Label(self.left_frame, text=self.hotel_location, font=("Arial", 16), bg='lightgrey').pack(padx=10, pady=5)

        tk.Label(self.left_frame, text="Served by:").pack(padx=10, pady=5)
        self.waiter_name_entry = tk.Entry(self.left_frame)
        self.waiter_name_entry.pack(padx=10, pady=5)

        tk.Label(self.left_frame, text="Item:").pack(padx=10, pady=5)
        self.item_var = tk.StringVar(self.left_frame)
        self.item_var.set(next(iter(self.prices)))  # default value
        self.item_menu = tk.OptionMenu(self.left_frame, self.item_var, *self.prices.keys())
        self.item_menu.pack(padx=10, pady=5)

        tk.Label(self.left_frame, text="Quantity:").pack(padx=10, pady=5)
        self.item_quantity_entry = tk.Entry(self.left_frame)
        self.item_quantity_entry.pack(padx=10, pady=5)

        self.add_item_button = tk.Button(self.left_frame, text="Add Item", command=self.add_item)
        self.add_item_button.pack(pady=10)

        self.item_listbox = tk.Listbox(self.left_frame, width=40, height=4)
        self.item_listbox.pack(padx=10, pady=10)

        self.calculate_button = tk.Button(self.left_frame, text="Calculate Total", command=self.calculate_total)
        self.calculate_button.pack(pady=10)

        tk.Label(self.left_frame, text="Payment Amount:").pack(padx=10, pady=5)
        self.payment_entry = tk.Entry(self.left_frame)
        self.payment_entry.pack(padx=10, pady=5)

        self.balance_label = tk.Label(self.left_frame, text="Balance Due: Ksh0.00")
        self.balance_label.pack(pady=10)

        self.payment_button = tk.Button(self.left_frame, text="Process Payment", command=self.process_payment)
        self.payment_button.pack(pady=10)

        # Right frame widgets
        self.receipt_text = tk.Text(self.right_frame, width=40, height=20)
        self.receipt_text.pack(padx=10, pady=10)

        self.print_button = tk.Button(self.right_frame, text="Print Receipt", command=self.print_receipt)
        self.print_button.pack(pady=10)

    def add_item(self):
        item_name = self.item_var.get()
        try:
            quantity = int(self.item_quantity_entry.get())
            if item_name in self.prices:
                item_price = self.prices[item_name]
                total_price = item_price * quantity
                self.items.append((item_name, item_price, quantity, total_price))
                self.item_listbox.insert(tk.END, f"{item_name} x {quantity}: Ksh{total_price:.2f}")
                self.item_quantity_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Invalid Item", "Item not found in the price list.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity.")

    def calculate_total(self):
        sale_amount = sum(total for name, price, quantity, total in self.items)
        tax_amount = sale_amount * self.tax_rate
        total_amount = sale_amount + tax_amount

        self.generate_receipt(sale_amount, tax_amount, total_amount)

        # Calculate and display balance
        try:
            payment_amount = float(self.payment_entry.get())
            balance_due = payment_amount - total_amount
            self.balance_label.config(text=f"Balance Due: Ksh{balance_due:.2f}")
        except ValueError:
            self.balance_label.config(text="Balance Due: Ksh0.00")

    def process_payment(self):
        try:
            payment_amount = float(self.payment_entry.get())
            sale_amount = sum(total for name, price, quantity, total in self.items)
            tax_amount = sale_amount * self.tax_rate
            total_amount = sale_amount + tax_amount

            if payment_amount < total_amount:
                messagebox.showerror("Insufficient Payment", "Payment amount is less than the total amount.")
            else:
                balance_due = payment_amount - total_amount
                self.generate_receipt(sale_amount, tax_amount, total_amount, payment_amount, balance_due)
                self.balance_label.config(text=f"Balance Due: Ksh{balance_due:.2f}")
                messagebox.showinfo("Payment Successful", "Payment has been processed successfully.")
        except ValueError:
            messagebox.showerror("Invalid Payment", "Please enter a valid payment amount.")

    def generate_receipt(self, sale, tax, totals, amount_paid=None, balance_due=None):
        waiter_name = self.waiter_name_entry.get()

        # Receipt content
        receipt = (
            f"{self.hotel_location:^40}\n"
            f"{'Hotel Sale Receipt':^40}\n"
            f"{'-' * 40}\n"
            f"Served By: {waiter_name}\n"
            f"{'-' * 40}\n"
        )
        for name, price, quantity, total in self.items:
            receipt += f"{name:<20} x {quantity:<5} @ Ksh{price:>6.2f} each: Ksh{total:>7.2f}\n"
        receipt += (
            f"{'-' * 40}\n"
            f"{'Sale Amount:':<20} Ksh{sale:>16.2f}\n"
            f"{'10% VAT Amount:':<20} Ksh{tax:>16.2f}\n"
            f"{'Total Amount:':<20} Ksh{totals:>16.2f}\n"
        )
        if amount_paid is not None:
            receipt += f"{'Amount Paid:':<20} Ksh{amount_paid:>16.2f}\n"
        if balance_due is not None:
            receipt += f"{'Balance Due:':<20} Ksh{balance_due:>16.2f}\n"
        receipt += (
            f"{'-' * 40}\n"
            f"{'Welcome Again!':^40}\n"
        )
        # Update the receipt text widget in the right pane
        self.receipt_text.delete(1.0, tk.END)
        self.receipt_text.insert(tk.END, receipt)
        self.receipt = receipt

    def print_receipt(self):
        if hasattr(self, 'receipt'):
            pdf = FPDF()
            pdf.add_page()

            # Set up font for title
            pdf.set_font("Arial", size=12)

            # Add logo image (centered)
            try:
                image_width = 30  # Width of the image
                pdf.image("images/images.png", x=(pdf.w - image_width) / 2, y=10, w=image_width)  # Center image
            except Exception as e:
                messagebox.showerror("PDF Error", f"Failed to load image for PDF: {e}")

            # Add space for title below the image
            pdf.ln(30)  # Adjust the spacing as needed

            # Add the bold title below the image (centered)
            pdf.set_font("Arial", style='B', size=24)  # Bold and large title
            pdf.cell(0, 10, txt=self.hotel_name, ln=True, align='C')

            # Add space below the title
            pdf.ln(10)

            # Add receipt content, centered
            pdf.set_font("Arial", size=12)
            for line in self.receipt.split('\n'):
                pdf.cell(0, 10, txt=line, ln=True, align='C')

            pdf_file = "Hotel_Sale_Receipt.pdf"
            pdf.output(pdf_file)

            if os.path.exists(pdf_file):
                # Print the PDF file using system's default print command
                os.system(f"lpr {pdf_file}")
                messagebox.showinfo("Print", "Receipt has been sent to the printer.")
            else:
                messagebox.showerror("File Not Found", "PDF file not found. Please generate the receipt first.")
        else:
            messagebox.showerror("No Receipt", "Please generate a receipt first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelSaleApp(root)
    root.mainloop()
