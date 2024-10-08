import pandas as pd
import boto3
import json
from datetime import datetime
from collections import defaultdict
from utils.get_data import *
from exports.template import template_xlsx
import base64
import jpype
jpype.startJVM()
from asposecells.api import *

config = {
    "dynamodb_endpoint": "http://localhost:8000",
}
dynamodb = boto3.resource('dynamodb', endpoint_url=config['dynamodb_endpoint'])

# ฟังก์ชันสำหรับตั้งค่าเอกสาร Excel (เช่น การเพิ่มหัวกระดาษและการป้อนข้อมูล)
def set_paper(sheet_name: str, writer: pd.ExcelWriter, user_name: str, len_template: int):
    worksheet = writer.sheets[sheet_name]
    now = datetime.now()
    thai_year = now.year + 543
    thai_date = now.strftime(f'%d/%m/{thai_year}')
    footer_left = f'&L Users : {user_name}'
    footer_right = f'&R Create At : {thai_date}'
    footer_center = f'&C หน้าที่ &P / &N'
    worksheet.set_footer(footer_left + footer_center + footer_right)
    worksheet.freeze_panes(len_template+2, 0)

# ฟังก์ชันสำหรับเพิ่มสไตล์ในข้อมูล Excel
def add_style(dataframe: pd.DataFrame, styles: dict, writer: pd.ExcelWriter, len_template, custom_header, header_style, header_titles, file, sheet_name: str):
    if styles:
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        custom_styles = {}
        for style_key, style_value in styles.items():
            custom_styles[style_key] = workbook.add_format(style_value)

        columns_to_border = dataframe.columns
        columns_format = workbook.add_format({'border': 0, 'font_color': 'white', 'align' : 'right'})

        for col in columns_to_border:
            worksheet.write(0, dataframe.columns.get_loc(col), col, columns_format)

        for style_key, style_value in styles.items():
            for col_num, column in enumerate(dataframe.columns):
                amount_row = dataframe[column].__len__()
                if column == style_key:
                    for row_num, value in enumerate(dataframe[column], start=1):
                        if row_num >= len_template + 1:
                            style = get_style_in_list(column+"_last", custom_styles) if row_num == amount_row else get_style_in_list(column, custom_styles)
                            worksheet.write(row_num, col_num, dataframe[column][row_num-1], style)
                        if file == 'RPCL001':
                            claim_amount = dataframe.get('claim_amount')
                            payout_amount = dataframe.get('payout_amount')

                            if claim_amount is not None and payout_amount is not None:
                                if ('(' in str(dataframe.at[row_num-1, 'payout_amount'])) and dataframe.at[row_num-1, 'payout_amount'] != 0:
                                    red_font_style = workbook.add_format({'font_color': 'red','font_size': 9, 'num_format': '#,##0.00', 'border': 1,'text_wrap' : True, 'valign': 'top', 'align': 'right'})
                                    worksheet.write(row_num, dataframe.columns.get_loc('payout_amount'), dataframe.at[row_num-1, 'payout_amount'], red_font_style)

        add_style_column(worksheet, header_style, header_titles, writer, dataframe)
        merge_cells(worksheet, dataframe, len(dataframe.columns), custom_header, writer)

# ฟังก์ชันสำหรับเพิ่มสไตล์ที่ระบุในคอลัมน์
def add_style_column(worksheet, header_style, header_titles, writer, dataframe):
    workbook = writer.book
    column_style_map = {}
    for style_entry in header_style:
        columns = style_entry.get('column', [])
        style = workbook.add_format(style_entry.get('style', {}))
        for column in columns:
            column_style_map[column] = style

    for col_num, column in enumerate(dataframe.columns):
        for row_num, value in enumerate(dataframe[column], start=1):
            header_format = column_style_map.get(column)
            if value in header_titles:
                worksheet.write(row_num, col_num, value, header_format)

# ฟังก์ชันสำหรับรวมเซลล์ที่มีค่าเหมือนกัน   
def merge_cells(worksheet, dataframe, min_consecutive, custom_header, writer):
    workbook = writer.book
    add_header_values = [item['add_header'] for item in custom_header if isinstance(item, dict) and 'add_header' in item]
    add_header_styles = [workbook.add_format(item['style']) for item in custom_header if isinstance(item, dict) and 'style' in item]
    
    num_rows, num_cols = dataframe.shape
    
    for row in range(num_rows):
        start_col = 0
        while start_col < num_cols:
            current_value = dataframe.iloc[row, start_col]

            if pd.isna(current_value):
                start_col += 1
                continue

            end_col = start_col
            while end_col + 1 < num_cols and dataframe.iloc[row, end_col + 1] == current_value:
                end_col += 1
            if end_col > start_col and (end_col - start_col + 1) >= min_consecutive:
                style_header = None
                for header, style in zip(add_header_values, add_header_styles):
                    if current_value == header and pd.notna(current_value):
                        style_header = style
                        break
                
                if style_header:
                    worksheet.merge_range(row + 1, start_col, row + 1, end_col, current_value, style_header)
                else:
                    worksheet.merge_range(row + 1, start_col, row + 1, end_col, current_value)
                
            start_col = end_col + 1

# ฟังก์ชันสำหรับการกำหนดสไตล์
def custom_style(style, style_format):
    styles_mapping = {}
    for header, style_name in style_format.items():
        if style_name in style:
            styles_mapping[header] = style[style_name]
    return styles_mapping

# ฟังก์ชันสำหรับการดึงสไตล์ที่ระบุจากรายการ
def get_style_in_list(column_name: str, styles: dict):
    style = styles.get(column_name)
    if not style:
        style = styles.get(column_name.split('_last')[0])
    return style

# ฟังก์ชันสำหรับการเพิ่มแถวว่าง
def add_space(pd_dataframe):
    num_rows = 1
    if num_rows <= 0:
        return pd_dataframe
    empty_rows = pd.DataFrame([[None] * len(pd_dataframe.columns)] * num_rows, columns=pd_dataframe.columns)
    
    pd_dataframe_with_space = pd.concat([empty_rows, pd_dataframe], ignore_index=True)
    
    return pd_dataframe_with_space

# ฟังก์ชันสำหรับการเพิ่มหัวข้อ
def add_header(pd_dataframe, header):
    header_df = pd.DataFrame([[header]* (len(pd_dataframe.columns))], columns=pd_dataframe.columns)
    concatenated_df = pd.concat([header_df, pd_dataframe], ignore_index=True)
    return concatenated_df

# ฟังก์ชันสำหรับการเรียกใช้ฟังก์ชันที่ระบุ
def start_function(functions_to_call, pd_dataframe):
    function_dict = {
        'add_space' : add_space,
        'add_header' : lambda df, header: add_header(df, header)
    }
    for func_info in reversed(functions_to_call):
        if isinstance(func_info, dict):
            func_name, arg = list(func_info.items())[0]
            func = function_dict.get(func_name)
            if func:
                pd_dataframe = func(pd_dataframe, arg)
        else:
            func = function_dict.get(func_info)
            if func:
                pd_dataframe = func(pd_dataframe)

    return pd_dataframe

# ฟังก์ชันสำหรับการจัดกลุ่มข้อมูลตามประเภทที่ระบุ
def group_export(data, filter, language='th'):
    grouped = defaultdict(list)
    if filter == 'insurance':
        for item in data:
            insurer_data = json.loads(item['insurer'])
            if 'en' in insurer_data.get('insurer_name', {}).get('M', {}):
                insurer_name = insurer_data.get('insurer_name', {}).get('M', {}).get('th', {}).get('S')
            else:
                insurer_name = insurer_data.get('insurer_name', {}).get('M', {}).get(language, {}).get('S')
            if insurer_name:
                grouped[insurer_name].append(item)

        result = [group for i, group in enumerate(grouped.values())]
        return result
    elif filter == 'product':
        for item in data:
            insurer_data = json.loads(item['loan_product'])
            insurer_name = insurer_data.get('name', {}).get('M', {}).get(language, {}).get('S')
            if insurer_name:
                grouped[insurer_name].append(item)

        result = [group for i, group in enumerate(grouped.values())]
        return result

# ฟังก์ชันหลักสำหรับการเรียกใช้งานการจัดกลุ่มข้อมูล
def split_data(data, chunk_size, group=False):
    if group:   
        flattened_list = []
        for item in data:
            split_data = [item[i:i + chunk_size] for i in range(0, len(item), chunk_size)]
            flattened_list.append(split_data)
        result = [inner for outer in flattened_list for inner in outer]
        return result
    else:
        result = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        return result

# ตั้งชื่อชีทตามประเภทของฟิลเตอร์
def set_sheet_name(data_transaction, filter_type):
    if filter_type == 'insurance':
        for item in data_transaction:
            insurance_company = item.get("insurance_company", '')
            return insurance_company
    elif filter_type == 'product':
        for item in data_transaction:
            loan_id = item.get("loan_id", '')
            return loan_id

# สร้างไฟล์ Excel ตามข้อมูลและเทมเพลตที่กำหนด
def gen_excel(template_data, template, filter_items = None):
    template_input = template_xlsx(template, filter_items)
    user_name = template_input['user_name']

    filter_type = template_input.get('filter', None)
    file_name = template_input.get('file_name', '')
    language = template_input.get('language')

    if filter_type == None:
        group = False
    else:
        filter = template_input['filter']
        group = True
    
    if filter_type is None:
        file_name = f'{file_name}.xlsx'
    else:
        suffix = ''
        if filter_type == 'insurance':
            suffix = '_insurance'
        elif filter_type == 'product':
            suffix = '_product'
        file_name = f'{file_name}{suffix}.xlsx'


    if template_input['table'] == 'insurance_company_report':
        table = dynamodb.Table('insurance_company_report')
        response = table.scan()
        items = response['Items']
        data = object_RPCL002(items)
    elif template_input['table'] == 'claims_cause_analysis_report':
        table = dynamodb.Table('claims_cause_analysis_report')
        response = table.scan()
        items = response['Items']
        data = object_RPCL003(items)
    else:
        data = template_data

    if group and template_input['table'] == 'sales_premium_transaction':
        data = group_export(data, filter, language)
        chunks = data
    else:
        chunks = [data]

    with pd.ExcelWriter(f'./pdf_xlsx/{file_name}', engine='xlsxwriter') as writer:
        for i, chunk in enumerate(chunks):
            if template_input['table'] == 'sales_premium_transaction':
                data_transaction = get_customer_report(chunk, language)
            elif template_input['table'] == 'insurance_company_report':
                data_transaction = get_insurance_company_report(chunk)
            elif template_input['table'] == 'claims_cause_analysis_report':
                data_transaction = get_claims_cause_analysis_report(chunk)
            pd_dataframe = pd.DataFrame(data_transaction)

            header_titles = [item['variable'] for item in template_input['output_header']]
            header_dict = {item['variable']: item['title'] for item in template_input['output_header']}
            pd_dataframe.rename(columns=header_dict, inplace=True)

            style = custom_style(template_input['style'], template_input['style_format'])
            header_row = pd.DataFrame([header_titles], columns=pd_dataframe.columns)
            pd_dataframe = pd.concat([header_row, pd_dataframe], ignore_index=True)

            pd_dataframe = start_function(template_input['excel_template'], pd_dataframe)
            if group:
                sheet_name = f'{set_sheet_name(data_transaction, filter_type)}'
                export_xlsx(pd_dataframe, writer, sheet_name=sheet_name)
            else:
                sheet_name = f'Sheet_{i+1}'
                export_xlsx(pd_dataframe, writer, sheet_name=sheet_name)
            # เพิ่มสไตล์
            len_template = len(template_input['excel_template'])
            custom_header = template_input['excel_template']
            header_style = template_input['header_style']
            file = template_input['file_name']
            add_style(pd_dataframe, style, writer, len_template, custom_header, header_style, header_titles, file, sheet_name=sheet_name)
            # เพิ่มฟุตเตอร์
            set_paper(sheet_name, writer, user_name, len_template)
            worksheet = writer.sheets[sheet_name]
            if template_input['table'] == 'sales_premium_transaction' or template_input['table'] == 'claims_cause_analysis_report':
                worksheet.set_portrait()
            elif template_input['table'] == 'insurance_company_report':
                worksheet.set_landscape()
            worksheet.center_horizontally()
            worksheet.set_margins(left=0.25, right=0.25)

            worksheet.set_paper(9)
            for col_num, column in enumerate(pd_dataframe.columns):
                if column != 'number':
                    worksheet.set_column(col_num, col_num, template_input['set_column'])
                else:
                    worksheet.set_column(col_num, col_num, 5)

    base64_string = file_to_base64(f'./pdf_xlsx/{file_name}')
    base64_to_file(base64_string, f'./pdf_xlsx/{file_name}')

# ฟังก์ชันสำหรับส่งออกข้อมูลไปยังไฟล์ Excel
def export_xlsx(dataframe: pd.DataFrame, writer: pd.ExcelWriter, sheet_name: str, xlsx_index: bool = False):
    if len(dataframe.index) != 0:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=xlsx_index)
    else:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=xlsx_index)

"""แปลงไฟล์ xlsx เป็นไฟล์ xls"""
# ฟังก์ชันสำหรับแปลงไฟล์เป็น base64
def file_to_base64(file_path):
    print(file_path)
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

# ฟังก์ชันสำหรับแปลง base64 กลับเป็นไฟล์
def base64_to_file(base64_string, output_file_path):
    output_file_path = output_file_path.replace('.xlsx', '.xls')
    with open(output_file_path, "wb") as file:
        file.write(base64.b64decode(base64_string))
