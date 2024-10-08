# Export PDF
file นี้ทำการสร้างไฟล์ PDF จาก DataFrame ของ Pandas ซึ่งมีการจัดรูปแบบตาม template ที่กำหนดไว้ โดยใช้ไลบรารี `FPDF` นี่คือรายละเอียดขององค์ประกอบหลัก:

1. **`TABLE_dataframe`**:
   - แปลง DataFrame ของ Pandas เป็น tuple ของแถวที่จัดรูปแบบ รวมถึงส่วนหัวที่สามารถใช้ใน PDF ได้

2. **`multi_cell_row`**:
   - วาดแถวของเซลล์ใน PDF จัดการกับการจัดรูปแบบข้อความ การแบ่งบรรทัด และเส้นขอบของเซลล์ รองรับรูปแบบและการจัดตำแหน่งตามที่กำหนด

3. **Class `PDF`**:
   - เป็นคลาสย่อยของ `FPDF` ที่ใช้สร้างไฟล์ PDF พร้อมส่วนหัวและส่วนท้ายที่กำหนดเอง รวมถึงฟังก์ชันในการใส่เนื้อหาที่เปลี่ยนแปลงได้ (เช่น ชื่อผู้ใช้และวันที่ปัจจุบัน) ในส่วนท้าย

4. **`generate_pdf_from_dataframe`**:
   - ฟังก์ชันหลักที่รับ DataFrame และสร้างไฟล์ PDF โดยใช้ฟังก์ชัน `TABLE_dataframe` เพื่อแปลง DataFrame เป็นแถว แล้วแสดงผลใน PDF โดยใช้ฟังก์ชัน `multi_cell_row`
   - ฟังก์ชันนี้ใช้เทมเพลตสำหรับกำหนดความกว้างของเซลล์ ความสูงของแถว และรูปแบบสำหรับส่วนหัวและข้อมูลของแต่ละแถว ทั้งนี้ การกำหนดหน้ากระดาษจะถูกตั้งเป็นแนวตั้งหรือแนวนอนขึ้นอยู่กับค่า `file_name`

ตัวอย่าง template PDF
```
template_input = {
            'file_name' : 'RPCL001',
            'language' : 'th',
            'table' : 'sales_premium_transaction',
            'user_name' : 'test test',
            'set_column' : 11,
            'cell_widths' : [10, 23, 23, 23, 23, 23, 23, 23, 23],
            'row_height' : 5,
            'columns_styles' : [
                {'columns': 'id', 'style': {'font_size': 10 , 'bold' : 'B', 'color' : (230, 247, 255), 'bg_color' : (230, 247, 255)}},
                {'columns': 'customer_name', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'loan_id', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'insurance_company', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'claim_amount', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'claim_status', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'submission_date', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'approval_date', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
                {'columns': 'payout_amount', 'style': {'font_size': 10, 'bold' : 'B', 'bg_color' : (230, 247, 255)}},
            ],
            'header_mapping' : {
                'id' : 'ID\n ',
                'customer_name': 'Customer Name\n ',
                'loan_id': 'Loan ID\n ',
                'insurance_company': 'Insurance Company',
                'claim_amount': 'Claim Amount\n ',
                'claim_status': 'Claim Status\n ',
                'submission_date': 'Submission Date\n ',
                'approval_date': 'Approval Date\n ',
                'payout_amount': 'Payout Amount\n '
            },
            'rows_styles' : [
                {'rows': 'id', 'style': {'font_size': 10, 'align': 'C'}},
                {'rows': 'customer_name', 'style': {'font_size': 10}},
                {'rows': 'loan_id', 'style': {'font_size': 10}},
                {'rows': 'insurance_company', 'style': {'font_size': 10}},
                {'rows': 'claim_amount', 'style': {'font_size': 10, 'align': 'R'}},
                {'rows': 'claim_status', 'style': {'font_size': 10}},
                {'rows': 'submission_date', 'style': {'font_size': 10, 'align': 'R'}},
                {'rows': 'approval_date', 'style': {'font_size': 10, 'align': 'R'}},
                {'rows': 'payout_amount', 'style': {'font_size': 10, 'align': 'R'}},
            ],
            'header_template': [
                {'header': 'รายงานการเรียกร้องตามลูกค้า (Claims by Customer Report)', 'style' : {'font_size' : 16}},
                {'header': 'ข้อมูลระหว่างวันที่ 01/07/2567 - 20/07/2567', 'style': {'font_size' : 10}}
            ]
        }
```
# รายละเอียดการทำงานของโค้ด Export excel (xlsx,xls)
ใช้สำหรับการสร้างไฟล์ excel ออกมาโดยที่เราสามารถกำหนดรูปแบบของ template ได้ด้วยตัวเอง

1. **`gen_excel`**:
ในส่วนนี้จะทำการรับข้อมูลจาก template มาเพื่อกำหนด language ภาษาใน excel , file_name ชื่อไฟล์ที่ของเรา , filter_type นี่จากตัวอย่างจะมาในรูปแบบของการแยก ประเภทของข้อมูล หลังจากนั้นเราจะนำข้อมูลที่ได้จาก database มามัดรวมมาอยู่ในรูปแบบของ `DataFrame` โดยที่เราทำอย่างนี้จะทำให้ไฟล์ใน excel ชื่อ column จะทำการจัดเรียงข้อมูลได้ง่ายขึ้น

2. **`export_xlsx`**:
มีหน้าที่ในการสร้างไฟล์ excel ตามข้อมูลจาก `DataFrame` ขึ้นมา
2. **`add_style`**:
มีหน้าที่ในเพิ่ม style เข้าไปที่ excel โดยจะอิงจาก config ใน template มาเราสามารถกำหนดว่าให้เอา column หรือ row ไหนบ้างที่ต้องการเพิ่ม style เข้าไป
3. **`set_paper`**:
มีหน้าที่ในเพิ่ม เพิ่มหัวกระดาษของไฟล์ excel
4. **`file_to_base64`**:
จะใช้สำหรับการเปลี่ยนจากไฟล์ xlsx ไป xls โดยการเปลี่ยนไฟล์ xlsx เป็น base64
5. **`base64_to_file`**:
จะใช้สำหรับการเอา base64 เปลี่ยนไปเป็นไฟล์ xls
6. **`custom_style`**:
จะเป็นฟังชั่นที่ทำก่อนเริ่มฟังชั่น `add_style` โดยการจำแนก style ของแต่ละ column

ตัวอย่าง template
```
template_input = {
            'file_name' : 'RPCL001',
            'data_per_page' : 1000,
            'filter' : filter_items,
            'language' : 'th',
            'table' : 'sales_premium_transaction',
            'user_name' : 'test test',
            'set_column' : 11,
            'output_header': [
                {'title': 'number', 'variable': ' '},
                {'title': 'customer_name', 'variable': 'Customer Name'},
                {'title': 'loan_id', 'variable': 'Loan ID'},
                {'title': 'insurance_company', 'variable': 'Insurance Company'},
                {'title': 'claim_amount', 'variable': 'Claim Amount'},
                {'title': 'claim_status', 'variable': 'Claim Status'},
                {'title': 'submission_date', 'variable': 'Submission Date'},
                {'title': 'approval_date', 'variable': 'Approval Date'},
                {'title': 'payout_amount', 'variable': 'Payout Amount'}
            ],
            'header_style' : [
                {
                    'column' : ['number','claim_amount','payout_amount','submission_date','approval_date','customer_name','loan_id','insurance_company','claim_status'], 
                    'style' : {'align': 'center', 'valign': 'top', 'border': 1, 'font_size': 9, 'bold' : 1,'fg_color' :'#E6F7FF','text_wrap' : True}
                }
            ],
            'style': {
                'style_align_right': {'align': 'right', 'border': 1, 'font_size': 9,'text_wrap' : True, 'valign' : 'top'},
                'style_border': {'font_size': 9, 'border': 1,'text_wrap' : True, 'valign' : 'top'},
                'style_number': {'font_size': 9, 'num_format': '#,##0.00', 'border': 1,'text_wrap' : True, 'valign' : 'top', 'align' : 'right'},
                'style_index': {'font_size': 10, 'border': 1, 'valign' : 'top', 'align' : 'center'},
                'center_header' : {'font_size': 15, 'bold' : 1, 'align' : 'center', 'valign' : 'top'}
            },
            'style_format': {
                'number': 'style_index',
                'claim_amount': 'style_number',
                'payout_amount': 'style_number',
                'submission_date': 'style_align_right',
                'approval_date': 'style_align_right',
                'customer_name': 'style_border',
                'loan_id': 'style_border',
                'insurance_company': 'style_border',
                'claim_status': 'style_border'
            },
            'excel_template': [
                {'add_header': 'รายงานการเรียกร้องตามลูกค้า (Claims by Customer Report)', 'style': {'align' : 'center', 'bold' : '1', 'font_size' : 15}},
                'add_space',
                {'add_header': 'ข้อมูลระหว่างวันที่ 01/07/2567 - 20/07/2567', 'style': {'align' : 'center'}},
                'add_space'
            ]
        }
```

# รายละเอียดการทำงานของโค้ด PDFMapper
จะเก็บอยู่ใน folder Mapper
โค้ดนี้มีหน้าที่ในการอ่านและเขียน field ต่าง ๆ ที่อยู่ในไฟล์ PDF รวมถึงการสร้างไฟล์ PDF ใหม่ที่มีข้อมูลจาก data_fields มาใส่ลงใน field ต่าง ๆ ของไฟล์ต้นฉบับ แล้วรวมไฟล์ PDF ที่มีข้อมูลเข้ากับไฟล์เทมเพลตเดิม
## ขั้นตอนการทำงาน
### 1. ค้นหาชื่อ field ใน PDF (find_form_fields)
ใช้ฟังก์ชัน find_form_fields(pdf_path) เพื่อค้นหา field ในไฟล์ PDF โดยใช้ไลบรารี fitz (PyMuPDF) ทำการค้นหา field ต่าง ๆ เช่น ช่องกรอกข้อความ, เช็คบ็อกซ์, ปุ่มตัวเลือก และจะระบุตำแหน่ง (พิกัด) และขนาดของแต่ละ field ลงในรายการ form_fields พร้อมแก้ไขชื่อ field หากพบชื่อซ้ำกัน
### 2. เปลี่ยนชื่อ field (change_field_name)
ฟังก์ชัน change_field_name ใช้สำหรับเปลี่ยนชื่อ field ที่มีชื่อซ้ำกัน เช่นในกรณีที่มีเช็คบ็อกซ์หลายตัวที่ใช้ชื่อเดียวกัน จะเพิ่มเลขต่อท้ายชื่อเช่น field_1, field_2 เพื่อให้สามารถแยกได้
### 3. สร้างไฟล์ PDF ที่มีข้อมูล map ลงใน field (create_pdf_with_data)
ฟังก์ชัน create_pdf_with_data ใช้สร้างไฟล์ PDF ที่นำข้อมูลจาก data_fields ไปแทรกลงในตำแหน่ง field ที่กำหนดในไฟล์ PDF โดยมีการจัดรูปแบบข้อความ, รูปภาพ และเช็คบ็อกซ์ตามข้อมูลที่ระบุ
### 4. หา field  checkbox ที่ซ้ำกัน `(process_data_fields)`
ฟังก์ชัน process_data_fields ใช้สำหรับจัดการค่า field ที่ซ้ำกัน โดยเฉพาะ field ที่เป็นเช็คบ็อกซ์ เพื่อให้ field หลักและ field ย่อยที่มี suffix (เช่น _1, _2) ทำงานสัมพันธ์กัน
### 5. รวม PDF template กับ PDF data `(merge_pages)`
ฟังก์ชัน merge_pages ใช้สำหรับรวมไฟล์ PDF ที่มีข้อมูลที่แทรกลงใน field กับไฟล์เทมเพลตต้นฉบับเข้าด้วยกัน โดยหน้าของทั้งสองไฟล์จะถูกซ้อนทับและรวมเป็นไฟล์เดียว

# รายละเอียดการทำงานของโค้ด PDFMapper V2
โค้ดนี้มีการจัดการกับฟิลด์ในไฟล์ PDF โดยใช้ไลบรารี fitz (PyMuPDF) เพื่อค้นหาฟิลด์ต่าง ๆ (เช่น ช่องกรอกข้อความ, เช็คบ็อกซ์, หรือฟิลด์รูปภาพ) จากนั้นจะนำข้อมูลจากตัวแปร data_fields ไปใส่ในตำแหน่งที่กำหนดในไฟล์ PDF ที่เลือกมา และสร้างไฟล์ PDF ใหม่โดยมีข้อมูลที่ถูกใส่ลงไปในฟิลด์ จากนั้นจะลบฟิลด์ในไฟล์ PDF ที่สร้างขึ้นเพื่อไม่ให้สามารถแก้ไขฟิลด์ได้อีก

จะทำงานคล้ายกับ PDFMapper อันแรกแต่จะเปลี่ยนจากการที่เอาไฟล์ต้นฉบับกับข้อมูลมา merge กัน จะใช้วิธีเขียนข้อมูลลงไปในไฟล์ต้นฉบับเลย แล้วจะทำการลบ field ในไฟล์ต้นฉบับและจะทำการ save ไฟล์
## ขั้นตอนการทำงาน
### 1. ค้นหาชื่อ field ใน PDF `(find_form_fields)`
ใช้สำหรับค้นหาและดึงข้อมูลฟิลด์ต่าง ๆ ที่อยู่ในไฟล์ PDF โดยจะดึงชื่อฟิลด์, ประเภทฟิลด์ (เช่น TextField, Checkbox, ImageField), ตำแหน่งของฟิลด์ในเอกสาร รวมถึงขนาดของฟิลด์นั้นๆ
### 2. ฟังก์ชัน `create_pdf_with_data`
ใช้เพื่อใส่ข้อมูลลงในฟิลด์ที่ค้นหามาจาก find_form_fields โดยใช้ข้อมูลจาก data_fields ข้อมูลนี้อาจเป็นข้อความ, เช็คบ็อกซ์, หรือรูปภาพ ซึ่งจะถูกแทรกลงในตำแหน่งฟิลด์ของไฟล์ PDF ที่สร้างขึ้น
### 3. ฟังก์ชัน `remove_fields_from_pdf`
ใช้เพื่อทำการลบฟิลด์ทั้งหมดออกจากไฟล์ PDF ที่สร้างขึ้น ทำให้ไม่สามารถแก้ไขฟิลด์เหล่านั้นได้อีก
## การใช้งาน:
1.เตรียมไฟล์ PDF ที่มีฟิลด์ (เช่น ฟิลด์กรอกข้อมูล, ฟิลด์เช็คบ็อกซ์, หรือฟิลด์รูปภาพ) โดยฟิลด์เหล่านี้จะถูกค้นหาและใส่ข้อมูลลงไป
2.กำหนดข้อมูลในตัวแปร data_fields ให้ตรงกับชื่อฟิลด์ในไฟล์ PDF

# Folder fonts
จะใช้าำหรับเก็บ fonts จะนำไปใช้
# Folder exports
เก็บฟังชั่นในการ export file xlsx และ pdf
# Folder PDF template
จะใช้เก็บ template pdf ที่จะใช้กับฟังชั่น `PDFMapper` และ `PDFMapper_V2`
# Folder Mapper
จะใช้เก็บฟังชั่น Mapper ที่จะทำการสร้างไฟล์ PDF
