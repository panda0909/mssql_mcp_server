import asyncio
import logging
import os
import pymssql
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl
import sys
# Set system encoding to UTF-8
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
# Configure logging
log_file = 'mssql_mcp_server.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        #logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # 保持控制台輸出
    ]
)
logger = logging.getLogger("mssql_mcp_server")

def get_db_config():
    """Get database configuration from environment variables."""
    # 檢查並記錄環境變數
    logger.info(f"環境變數: MSSQL_SERVER={os.getenv('MSSQL_SERVER')}, MSSQL_USER={os.getenv('MSSQL_USER')}, MSSQL_DATABASE={os.getenv('MSSQL_DATABASE')}")
    
    # 同時檢查 MSSQL_USERNAME (可能是 .env 檔案中使用的名稱)
    username = os.getenv("MSSQL_USER") or os.getenv("MSSQL_USERNAME", "reader")
    logger.info(f"使用者名稱變數: MSSQL_USERNAME={os.getenv('MSSQL_USERNAME')}")
    
    config = {
        "server": os.getenv("MSSQL_SERVER", "10.1.6.61"),
        "user": username,
        "password": os.getenv("MSSQL_PASSWORD", "reader"),
        "database": os.getenv("MSSQL_DATABASE", "JPC_PLM")
    }
    
    logger.info(f"使用的資料庫設定: {config['server']}/{config['database']} as {config['user']}")
    
    if not all([config["server"], config["user"], config["password"], config["database"]]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("MSSQL_SERVER, MSSQL_USER/MSSQL_USERNAME, MSSQL_PASSWORD, and MSSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")
    
    return config

# Initialize server
app = Server("mssql_mcp_server")

@app.list_resources()
async def list_resources() -> list[Resource]:
    """Aras System List SQL Server tables as resources."""
    config = get_db_config()
    try:
        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        # Query to get user tables from the current database
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = cursor.fetchall()
        logger.info(f"Found tables: {tables}")
        
        resources = []
        for table in tables:
            resources.append(
                Resource(
                    uri=f"mssql://{table[0]}/data",
                    name=f"Table: {table[0]}",
                    mimeType="text/plain",
                    description=f"Data in table: {table[0]}"
                )
            )
        cursor.close()
        conn.close()

        # Add additional string resources for query information
        resources.append(
            Resource(
            uri="mssql://query_help",
            name="SQL Query Help",
            mimeType="text/plain",
            description="Information about available tables and their schemas"
            )
        )
        
        # Add detailed schema information as a separate resource
        # Store the schema as a properly escaped JSON string
        schema_info = """
        {"itemtypes":[{"name":"CAD","label":"CAD Document","label_zt":"工程圖","properties":[{"name":"authoring_tool","label":"Authoring Tool","label_zt":"編輯工具","data_type":"list","reference_itemname":"Authoring Tools"},{"name":"authoring_tool_version","label":"Authoring Tool Version","label_zt":"編輯工具版本","data_type":"string","reference_itemname":null},{"name":"bcs_autonumber","label":"Number","label_zt":"正式圖號","data_type":"string","reference_itemname":null},{"name":"bcs_isrestricted","label":"Project Restricted","label_zt":"專案專屬","data_type":"boolean","reference_itemname":null},{"name":"bcs_ref_current_state_label","label":"State","label_zt":"系統狀態","data_type":"foreign","reference_itemname":null},{"name":"classification","label":"Type","label_zt":"工程圖類別","data_type":"string","reference_itemname":null},{"name":"cn_created_name","label":"Agile Creator","label_zt":"Agile建立者","data_type":"string","reference_itemname":null},{"name":"cn_cust","label":"Customer","label_zt":"客戶","data_type":"item","reference_itemname":"Customer"},{"name":"cn_dev_phase","label":"Development Phasent Phase","label_zt":"開發階段","data_type":"list","reference_itemname":"CAD_Development Phase"},{"name":"cn_drawing_version","label":"Drawing Version","label_zt":"圖紙版本","data_type":"string","reference_itemname":null},{"name":"cn_factory","label":"Factory","label_zt":"廠區","data_type":"list","reference_itemname":"Part_Factory"},{"name":"cn_iso","label":"ISO Number","label_zt":"ISO 編號","data_type":"string","reference_itemname":null},{"name":"cn_lifecycle","label":"Lifecycle Phase","label_zt":"Lifecycle Phase","data_type":"list","reference_itemname":"Doc_LifecyclePhase"},{"name":"cn_old_project","label":"Old Project","label_zt":"舊專案代號","data_type":"item","reference_itemname":"Old Project"},{"name":"cn_project_number","label":"Project Number","label_zt":"專案代號","data_type":"foreign","reference_itemname":null},{"name":"cn_revision","label":"Revision","label_zt":"工程圖版本","data_type":"string","reference_itemname":null},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"description","label":"Description","label_zt":"描述","data_type":"text","reference_itemname":null},{"name":"effective_date","label":"Effective Date","label_zt":"生效日期","data_type":"date","reference_itemname":null},{"name":"has_change_pending","label":"Changes","label_zt":"變更中","data_type":"boolean","reference_itemname":null},{"name":"is_standard","label":"Standard","label_zt":"標準件","data_type":"boolean","reference_itemname":null},{"name":"is_template","label":"Template","label_zt":"範本","data_type":"boolean","reference_itemname":null},{"name":"item_number","label":"Document Number","label_zt":"編號","data_type":"string","reference_itemname":null},{"name":"jpc_chkbom_gc","label":"Copy (2) of Check BOM GC-HF Error","label_zt":"檢查BOM是否GC-HF異常","data_type":"boolean","reference_itemname":null},{"name":"jpc_epb_pn","label":"EPB P/N","label_zt":"EPB P/N","data_type":"string","reference_itemname":null},{"name":"jpc_is_out_part","label":"Is outsourcing drawing","label_zt":"此為外購料號圖面","data_type":"boolean","reference_itemname":null},{"name":"jpc_part","label":"Related Part","label_zt":"零組件料號","data_type":"item","reference_itemname":"Part"},{"name":"jpc_part2","label":"Where used part","label_zt":"用於料號(排程更新)","data_type":"text","reference_itemname":null},{"name":"major_rev","label":"Revision","label_zt":"系統版本","data_type":"string","reference_itemname":null},{"name":"managed_by_id","label":"Designated User","label_zt":"管理者","data_type":"item","reference_itemname":"Identity"},{"name":"modified_by_id","label":"Modified By","label_zt":"修改人員","data_type":"item","reference_itemname":"User"},{"name":"modified_on","label":"Last Modified","label_zt":"修改日期","data_type":"date","reference_itemname":null},{"name":"name","label":"Name","label_zt":"名稱","data_type":"string","reference_itemname":null},{"name":"native_file","label":"Native File","label_zt":"原始檔案","data_type":"item","reference_itemname":"File"},{"name":"owned_by_id","label":"Owned By","label_zt":"設計繪圖者","data_type":"item","reference_itemname":"Identity"},{"name":"project","label":"Project","label_zt":"專案","data_type":"item","reference_itemname":"Project"},{"name":"release_date","label":"Release Date","label_zt":"發行日期","data_type":"date","reference_itemname":null},{"name":"state","label":"State","label_zt":"狀態","data_type":"string","reference_itemname":null},{"name":"team_id","label":"Team","label_zt":"團隊","data_type":"item","reference_itemname":"Team"},{"name":"thumbnail","label":"Thumbnail","label_zt":"縮圖","data_type":"image","reference_itemname":null},{"name":"viewable_file","label":"Viewable File","label_zt":"預覧檔案","data_type":"item","reference_itemname":"File"}]},{"name":"Customer","label":"Customer","label_zt":"客戶","properties":[{"name":"contact_name","label":"Contact Name","label_zt":"聯絡人","data_type":"string","reference_itemname":null},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"description","label":"Description","label_zt":"Description","data_type":"string","reference_itemname":null},{"name":"jpc_acc_industry_type","label":"Customer Industry Type","label_zt":"公司行業大類","data_type":"list","reference_itemname":"CompanyIndustryType"},{"name":"jpc_crm_id","label":"CRM_ID","label_zt":"CRM_ID","data_type":"string","reference_itemname":null},{"name":"jpc_erp_id","label":"ERP_ID","label_zt":"ERP_ID","data_type":"string","reference_itemname":null},{"name":"jpc_industry_2type","label":"Industry - type","label_zt":"行業-中分類","data_type":"list","reference_itemname":"jpc_industry_type"},{"name":"jpc_is_keyaccount","label":"KeyAccount","label_zt":"KeyAccount","data_type":"boolean","reference_itemname":null},{"name":"jpc_org_id","label":"ORG_ID","label_zt":"ORG_ID","data_type":"string","reference_itemname":null},{"name":"jpc_record","label":"CRM Record","label_zt":"CRM紀錄者","data_type":"string","reference_itemname":null},{"name":"jpc_source_type","label":"Source Type","label_zt":"公司來源","data_type":"list","reference_itemname":"Customer SourceType"},{"name":"main_phone","label":"Main Phone","label_zt":"電話","data_type":"string","reference_itemname":null},{"name":"managed_by_id","label":"Managed By","label_zt":"管理者","data_type":"item","reference_itemname":"Identity"},{"name":"modified_by_id","label":"Modified By","label_zt":"修改人員","data_type":"item","reference_itemname":"User"},{"name":"modified_on","label":"Modified On","label_zt":"修改日期","data_type":"date","reference_itemname":null},{"name":"name","label":"Name","label_zt":"客戶名稱","data_type":"string","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"擁有者","data_type":"item","reference_itemname":"Identity"},{"name":"sf_acc_id","label":"","label_zt":"sf_acc_id","data_type":"string","reference_itemname":null},{"name":"state","label":"State","label_zt":"狀態","data_type":"string","reference_itemname":null},{"name":"team_id","label":"Team","label_zt":"團隊","data_type":"item","reference_itemname":"Team"},{"name":"web_site","label":"Web Site","label_zt":"Web Site","data_type":"string","reference_itemname":null}]},{"name":"Document","label":"Document-JPC Internal","label_zt":"JPC-內部文件","properties":[{"name":"authoring_tool","label":"Authoring Tool","label_zt":"編輯軟體","data_type":"list","reference_itemname":"Authoring Tools"},{"name":"bcs_autonumber","label":"Number","label_zt":"正式文號","data_type":"string","reference_itemname":null},{"name":"bcs_ref_current_state_label","label":"State","label_zt":"系統狀態","data_type":"foreign","reference_itemname":null},{"name":"classification","label":"Type","label_zt":"文件類別","data_type":"string","reference_itemname":null},{"name":"cn__facility_location","label":"Facility Location","label_zt":"設備-存放地點","data_type":"string","reference_itemname":null},{"name":"cn__facility_mainten_cycle","label":"Facility Mainten Cycle","label_zt":"設備-保養週期","data_type":"list","reference_itemname":"Doc_Facility_Mainten_Cycle"},{"name":"cn__facility_mainten_dept","label":"Facility Mainten Dept","label_zt":"設備-保養單位","data_type":"string","reference_itemname":null},{"name":"cn__facility_mainten_lasttime","label":"Facility Mainten Lasttime","label_zt":"設備-上次保養日期","data_type":"date","reference_itemname":null},{"name":"cn__facility_mainten_nexttime","label":"Facility Mainten Nexttime","label_zt":"設備-下次保養日期","data_type":"date","reference_itemname":null},{"name":"cn__facility_mainten_other","label":"Facility Mainten Cycle Other (day)","label_zt":"其他週期(天)","data_type":"integer","reference_itemname":null},{"name":"cn__facility_model_number","label":"Facility Model Number","label_zt":"設備型號","data_type":"string","reference_itemname":null},{"name":"cn__facility_owner","label":"Facility Owner","label_zt":"生產設備 - 保管人","data_type":"item","reference_itemname":"Identity"},{"name":"cn__facility_owner_name","label":"Owner Name","label_zt":"生產設備 - 舊保管人","data_type":"string","reference_itemname":null},{"name":"cn__facility_type","label":"Facility Type","label_zt":"設備類別","data_type":"list","reference_itemname":"Doc_Facility_Type"},{"name":"cn_assets_number","label":"Assets Number","label_zt":"資產編號","data_type":"string","reference_itemname":null},{"name":"cn_factory","label":"Factory","label_zt":"廠區","data_type":"list","reference_itemname":"OPart_Factory"},{"name":"cn_green_product_expired_date","label":"Green Product Testing Report Expire Date","label_zt":"測試報告到期日期","data_type":"date","reference_itemname":null},{"name":"cn_green_product_expired_year","label":"Green Product Testing Report Vaild Year","label_zt":"測試報告有效年","data_type":"list","reference_itemname":"Doc_GPReportPeriod"},{"name":"cn_green_product_test_date","label":"Green Product Testing Report Date","label_zt":"測試報告日期","data_type":"date","reference_itemname":null},{"name":"cn_green_product_test_number","label":"Green Product TestingReport Number","label_zt":"測試報告編號","data_type":"string","reference_itemname":null},{"name":"cn_green_product_type","label":"Green Product Testing Report Type","label_zt":"測試報告類別","data_type":"list","reference_itemname":"Doc_GPReportCategory"},{"name":"cn_instrument_acquire_date","label":"Instrument Acquire Date","label_zt":"取得日期","data_type":"date","reference_itemname":null},{"name":"cn_instrument_check_cycle","label":"Instrument Check Cycle","label_zt":"校驗週期","data_type":"list","reference_itemname":"Doc_Instrument_Check_Cycle"},{"name":"cn_instrument_check_lasttime","label":"Instrument Check LastTime","label_zt":"上次校驗日期","data_type":"date","reference_itemname":null},{"name":"cn_instrument_check_nexttime","label":"Instrument Check NextTime","label_zt":"下次校驗日期","data_type":"date","reference_itemname":null},{"name":"cn_instrument_correction_type","label":"Instrument Correction Type","label_zt":"校正類別","data_type":"list","reference_itemname":"Doc_Instrument_Correction_Type"},{"name":"cn_instrument_dept","label":"Instrument Department","label_zt":"校驗單位","data_type":"string","reference_itemname":null},{"name":"cn_instrument_number","label":"Instrument Number","label_zt":"儀器編號","data_type":"string","reference_itemname":null},{"name":"cn_instrument_owner","label":"Instrument Owner","label_zt":"儀校-保管人","data_type":"item","reference_itemname":"Identity"},{"name":"cn_instrument_owner_name","label":"Instrument Owner Name","label_zt":"儀校-舊保管人","data_type":"string","reference_itemname":null},{"name":"cn_instrument_specific","label":"Instrument Specific","label_zt":"儀器規格","data_type":"string","reference_itemname":null},{"name":"cn_instrument_type","label":"Instrument Type","label_zt":"儀器類別","data_type":"list","reference_itemname":"Doc_Instrument_Type"},{"name":"cn_instrument_used_dept","label":"Instrument Used Department","label_zt":"儀校-使用單位","data_type":"string","reference_itemname":null},{"name":"cn_iso_doc_type","label":"ISO Doc Type","label_zt":"ISO文件類型","data_type":"list","reference_itemname":"Doc_ISO_Doc_Type"},{"name":"cn_iso_next_dly_date","label":"Next Dly Date","label_zt":"到期日期","data_type":"date","reference_itemname":null},{"name":"cn_iso_number","label":"ISO Number","label_zt":"ISO編號","data_type":"string","reference_itemname":null},{"name":"cn_iso_own_dept","label":"ISO Owned Department","label_zt":"ISO-制定部門","data_type":"string","reference_itemname":null},{"name":"cn_iso_owner","label":"ISO Owner","label_zt":"ISO-制定人","data_type":"item","reference_itemname":"Identity"},{"name":"cn_iso_owner_name","label":"ISO Owner Name","label_zt":"ISO-制定人名稱","data_type":"string","reference_itemname":null},{"name":"cn_iso_system","label":"ISO System","label_zt":"ISO體系","data_type":"list","reference_itemname":"Doc_ISO_System"},{"name":"cn_lifecycle","label":"Lifecycle Phase","label_zt":"Lifecycle Phase","data_type":"list","reference_itemname":"Doc_LifecyclePhase"},{"name":"cn_old_project","label":"Old Project","label_zt":"舊專案代號","data_type":"item","reference_itemname":"Old Project"},{"name":"cn_order_number","label":"Order Number","label_zt":"訂單號碼","data_type":"string","reference_itemname":null},{"name":"cn_owned_by_name","label":"Old Owned Name","label_zt":"Agile 建立者","data_type":"string","reference_itemname":null},{"name":"cn_patent_announce","label":"Announce Type","label_zt":"公告大類","data_type":"list","reference_itemname":"Part_AnnouncementType"},{"name":"cn_patent_announce_date","label":"Patent Announce Date","label_zt":"專利公告日","data_type":"date","reference_itemname":null},{"name":"cn_patent_asset_date","label":"Patent Asset Date","label_zt":"專利申請日","data_type":"date","reference_itemname":null},{"name":"cn_patent_asset_number","label":"Patent Asset Number","label_zt":"專利-申請號","data_type":"string","reference_itemname":null},{"name":"cn_patent_country","label":"Patent Country","label_zt":"專利國家","data_type":"list","reference_itemname":"cn_doc_patent_country"},{"name":"cn_patent_invalidation_date","label":"Patent Invalidation","label_zt":"專利-失效日期","data_type":"date","reference_itemname":null},{"name":"cn_patent_office","label":"Patent Office","label_zt":"專利事務所","data_type":"string","reference_itemname":null},{"name":"cn_patent_office_number","label":"Patent Office Number","label_zt":"專利事務所案號","data_type":"string","reference_itemname":null},{"name":"cn_patent_owner","label":"Patent Owner","label_zt":"專利發明人","data_type":"text","reference_itemname":null},{"name":"cn_patent_preview_file","label":"Patent preview","label_zt":"專利-預覽檔案","data_type":"item","reference_itemname":"File"},{"name":"cn_patent_product_state","label":"Patent Product State","label_zt":"專利-產品階段","data_type":"list","reference_itemname":"cn_doc_patent_part_state"},{"name":"cn_patent_productline","label":"ProductLine","label_zt":"專利-應用領域","data_type":"string","reference_itemname":null},{"name":"cn_patent_register_number","label":"Patent Register Number","label_zt":"註冊號/專利號","data_type":"string","reference_itemname":null},{"name":"cn_patent_state","label":"Patent State","label_zt":"專利狀態","data_type":"list","reference_itemname":"cn_doc_patent_state"},{"name":"cn_patent_type","label":"Patent Type","label_zt":"專利類型","data_type":"list","reference_itemname":"cn_doc_patent_type"},{"name":"cn_product_line","label":"Product Line(s)","label_zt":"Product Line(s)","data_type":"list","reference_itemname":"Doc_Item_Product_Selection_List"},{"name":"cn_revision","label":"Revision","label_zt":"文件版本","data_type":"string","reference_itemname":null},{"name":"cn_sony_doc_owner","label":"Sony Doc Owner","label_zt":"Sony-制定人","data_type":"item","reference_itemname":"Identity"},{"name":"cn_sony_doc_owner_name","label":"Sony Doc Owner","label_zt":"Sony-制定人名稱","data_type":"string","reference_itemname":null},{"name":"cn_sony_doc_owndept","label":"Sony Doc Owner Dept","label_zt":"Sony-制定部門","data_type":"string","reference_itemname":null},{"name":"cn_sony_doctype","label":"Sony Doc Type","label_zt":"Sony-文件類型","data_type":"list","reference_itemname":"Doc_Sony_Doc_Type"},{"name":"cn_vendor","label":"Vendor","label_zt":"供應商","data_type":"item","reference_itemname":"Vendor"},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"customer","label":"Customer","label_zt":"客戶名稱","data_type":"item","reference_itemname":"Customer"},{"name":"description","label":"Description","label_zt":"說明","data_type":"string","reference_itemname":null},{"name":"effective_date_2","label":"Effective Date","label_zt":"生效日期","data_type":"date","reference_itemname":null},{"name":"has_change_pending","label":"Changes","label_zt":"變更中","data_type":"boolean","reference_itemname":null},{"name":"has_files","label":"Files","label_zt":"附加附檔","data_type":"boolean","reference_itemname":null},{"name":"item_number","label":"Document Number","label_zt":"文件編號","data_type":"string","reference_itemname":null},{"name":"jpc_part","label":"Part","label_zt":"零組件料號","data_type":"item","reference_itemname":"Part"},{"name":"major_rev","label":"Revision","label_zt":"系統版本","data_type":"string","reference_itemname":null},{"name":"managed_by_id","label":"Managed By","label_zt":"管理者","data_type":"item","reference_itemname":"Identity"},{"name":"modified_by_id","label":"Modified By","label_zt":"修改人員","data_type":"item","reference_itemname":"User"},{"name":"modified_on","label":"Modified On","label_zt":"修改日期","data_type":"date","reference_itemname":null},{"name":"name","label":"Name","label_zt":"名稱","data_type":"string","reference_itemname":null},{"name":"owned_by_id","label":"Assigned Creator","label_zt":"編輯者","data_type":"item","reference_itemname":"Identity"},{"name":"project","label":"Project","label_zt":"專案","data_type":"item","reference_itemname":"Project"},{"name":"release_date","label":"Effective Date","label_zt":"發行日期","data_type":"date","reference_itemname":null},{"name":"state","label":"State","label_zt":"系統狀態","data_type":"string","reference_itemname":null},{"name":"team_id","label":"Team","label_zt":"團隊","data_type":"item","reference_itemname":"Team"},{"name":"thumbnail","label":"Thumbnail","label_zt":"縮圖","data_type":"image","reference_itemname":null}]},{"name":"ECN","label":"ECN","label_zt":"ECN-工程變更","properties":[{"name":"basis","label":"Basis","label_zt":"Basis","data_type":"list","reference_itemname":"Change Basis"},{"name":"change_reason","label":"Change Reason","label_zt":"變更原因","data_type":"text","reference_itemname":null},{"name":"classification","label":"ECN Type","label_zt":"ECN類別","data_type":"string","reference_itemname":null},{"name":"cn_change_category","label":"Change Category","label_zt":"Change Category","data_type":"list","reference_itemname":"Change Category"},{"name":"cn_change_cost","label":"Estimate Change Total Cost","label_zt":"估計變更總成本","data_type":"text","reference_itemname":null},{"name":"cn_change_suggest","label":"Change Suggest","label_zt":"變更時效建議","data_type":"list","reference_itemname":"Change Suggest"},{"name":"cn_change_suggest_comment","label":"Change Suggest Comment","label_zt":"變更時效補充說明","data_type":"text","reference_itemname":null},{"name":"cn_check","label":"Check","label_zt":"Check","data_type":"item","reference_itemname":"Identity"},{"name":"cn_meterial_stock_solution","label":"Meterial Stock Solution","label_zt":"庫存材料轉用處理方案說明","data_type":"text","reference_itemname":null},{"name":"cn_product_line","label":"Product Line(s)","label_zt":"Product Line(s)","data_type":"mv_list","reference_itemname":null},{"name":"cn_risk_assessment","label":"Risk Assessment","label_zt":"變更風險評估","data_type":"string","reference_itemname":null},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"customer_approval","label":"Customer Approval Required","label_zt":"需客戶確認","data_type":"boolean","reference_itemname":null},{"name":"description","label":"Description","label_zt":"變更內容","data_type":"text","reference_itemname":null},{"name":"effectivity_date","label":"Effectivity Date","label_zt":"生效日期","data_type":"date","reference_itemname":null},{"name":"implementation_plan","label":"Implementation Plan","label_zt":"執行計畫","data_type":"text","reference_itemname":null},{"name":"item_number","label":"ECN Number","label_zt":"ECN編號","data_type":"sequence","reference_itemname":null},{"name":"jpc_assigned_prodline","label":"TP-HF Dept","label_zt":"台北高頻產品部門","data_type":"list","reference_itemname":"JPC_TP_HF_Dept"},{"name":"jpc_ecn_follow","label":"ECN Follow","label_zt":"ECN跟進表","data_type":"string","reference_itemname":null},{"name":"jpc_error_message","label":"","label_zt":"系統錯誤","data_type":"text","reference_itemname":null},{"name":"jpc_file_import","label":"","label_zt":"在製/在途/在庫","data_type":"item","reference_itemname":"File"},{"name":"jpc_islock_ecn_affitem","label":"Lock ECN Affected Item","label_zt":"變更中鎖住 ECN料號","data_type":"boolean","reference_itemname":null},{"name":"jpc_required_file","label":"ECN Required Files","label_zt":"ECN 必要文件","data_type":"mv_list","reference_itemname":null},{"name":"jpc_trans_finished","label":"","label_zt":"是否已拋轉","data_type":"integer","reference_itemname":null},{"name":"major_rev","label":"Revision","label_zt":"版本","data_type":"string","reference_itemname":null},{"name":"managed_by_id","label":"Managed By","label_zt":"管理者","data_type":"item","reference_itemname":"Identity"},{"name":"modified_by_id","label":"Modified By","label_zt":"修改人員","data_type":"item","reference_itemname":"User"},{"name":"modified_on","label":"Modified On","label_zt":"修改日期","data_type":"date","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"提報人員","data_type":"item","reference_itemname":"Identity"},{"name":"priority","label":"Priority","label_zt":"級別","data_type":"list","reference_itemname":"Change Priorities"},{"name":"release_date","label":"Release Date","label_zt":"發行日期","data_type":"date","reference_itemname":null},{"name":"special_instructions","label":"Special Instructions","label_zt":"注意事項","data_type":"text","reference_itemname":null},{"name":"state","label":"Status","label_zt":"狀態","data_type":"string","reference_itemname":null},{"name":"team_id","label":"Team","label_zt":"團隊","data_type":"item","reference_itemname":"Team"},{"name":"title","label":"Title","label_zt":"主題內容","data_type":"string","reference_itemname":null}]},{"name":"ECR","label":"ECR","label_zt":"ECR變更通知單","properties":[{"name":"basis","label":"Basis","label_zt":"Basis","data_type":"list","reference_itemname":"Change Basis"},{"name":"change_type","label":"Change Type","label_zt":"變更類型","data_type":"list","reference_itemname":"Change Types"},{"name":"classification","label":"ECN Initial","label_zt":"ECN發行單位","data_type":"string","reference_itemname":null},{"name":"cn_change_category","label":"Change Category","label_zt":"Change Category","data_type":"list","reference_itemname":"Change Category"},{"name":"cn_change_reason","label":"Reason for Change","label_zt":"變更原因","data_type":"text","reference_itemname":null},{"name":"cn_change_suggest","label":"Change Suggest","label_zt":"變更時效建議","data_type":"list","reference_itemname":"Change Suggest"},{"name":"cn_description","label":"Change Description","label_zt":"變更說明","data_type":"text","reference_itemname":null},{"name":"cn_ecn_creator","label":"ECN Creator","label_zt":"ECN 建單者","data_type":"foreign","reference_itemname":null},{"name":"cn_ecn_info","label":"","label_zt":"ECN總結","data_type":"string","reference_itemname":null},{"name":"cn_ecn_number","label":"ECN Number","label_zt":"ECN編號","data_type":"item","reference_itemname":"ECN"},{"name":"cn_ecn_released_date","label":"ECN Released Date","label_zt":"ECN 結案完成日","data_type":"foreign","reference_itemname":null},{"name":"cn_is_modification","label":"Is Modification","label_zt":"是否需要修模","data_type":"list","reference_itemname":"Yes/No Cost List"},{"name":"cn_is_noti_customer","label":"Is Notification Customer","label_zt":"是否需要通知客人","data_type":"list","reference_itemname":"Yes/No Cost List"},{"name":"cn_is_verification","label":"Is Verification","label_zt":"是否驗證","data_type":"list","reference_itemname":"Yes/No Cost List"},{"name":"cn_product_line","label":"Product Line(s)","label_zt":"Product Line(s)","data_type":"list","reference_itemname":"Product Line"},{"name":"cn_reason_code","label":"Reason Code","label_zt":"申請原因代碼","data_type":"list","reference_itemname":"Reason Code"},{"name":"cn_resqu_user_dept","label":"Request Dept","label_zt":"需求單位","data_type":"foreign","reference_itemname":null},{"name":"cn_risk_assessment","label":"Risk Assessment","label_zt":"變更風險評估","data_type":"string","reference_itemname":null},{"name":"created_by_id","label":"Creator","label_zt":"建立人員","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"ecr_comments","label":"ECR Comments","label_zt":"結論","data_type":"text","reference_itemname":null},{"name":"fast_track","label":"Fast Track","label_zt":"快速變更","data_type":"boolean","reference_itemname":null},{"name":"item_number","label":"ECR Number","label_zt":"ECR 編號","data_type":"sequence","reference_itemname":null},{"name":"jpc_assigned_prodline","label":"TP-HF Dept","label_zt":"台北高頻產品部門","data_type":"list","reference_itemname":"JPC_TP_HF_Dept"},{"name":"jpc_chk_vn_part_result","label":"VN Part Result","label_zt":"VN料號確認結果","data_type":"boolean","reference_itemname":null},{"name":"jpc_message","label":"System Message-Customer Parts","label_zt":"系統通知-客戶料號變更","data_type":"text","reference_itemname":null},{"name":"jpc_message_vn_part","label":"System Noti - VN Part Change","label_zt":"系統通知-VN料號變更","data_type":"text","reference_itemname":null},{"name":"jpc_owner_dept","label":"Owner Dept","label_zt":"發起部門","data_type":"item","reference_itemname":"Identity"},{"name":"jpc_sales_manager","label":"Sales Manager","label_zt":"業務主管","data_type":"item","reference_itemname":"Identity"},{"name":"priority","label":"Priority","label_zt":"優先順序","data_type":"list","reference_itemname":"Change Priorities"},{"name":"release_date","label":"Release Date","label_zt":"ECR發行日期","data_type":"date","reference_itemname":null},{"name":"requested_by","label":"Requested By","label_zt":"需求人員","data_type":"item","reference_itemname":"Identity"},{"name":"source","label":"Source","label_zt":"需求來源","data_type":"list","reference_itemname":"Change Sources"},{"name":"state","label":"Status","label_zt":"狀態","data_type":"string","reference_itemname":null},{"name":"title","label":"Title","label_zt":"標題","data_type":"string","reference_itemname":null}]},{"name":"Express DCO","label":"EN","label_zt":"EN工程通知單","properties":[{"name":"bcs_ref_current_state_label","label":"State","label_zt":"狀態","data_type":"foreign","reference_itemname":null},{"name":"change_reason","label":"Reason for Change","label_zt":"變更原因","data_type":"text","reference_itemname":null},{"name":"classification","label":"Classification","label_zt":"類別","data_type":"string","reference_itemname":null},{"name":"cn_actual_creator","label":"Actual Creator","label_zt":"實際申請者","data_type":"item","reference_itemname":"Identity"},{"name":"cn_change_category","label":"Change Category","label_zt":"Change Category","data_type":"list","reference_itemname":"Change Category"},{"name":"cn_factory","label":"Factory","label_zt":"廠區","data_type":"list","reference_itemname":"Part_Factory"},{"name":"cn_meterial_stock_check","label":"Meterial Stock is not affected","label_zt":"庫存不受影響","data_type":"boolean","reference_itemname":null},{"name":"cn_meterial_stock_solution","label":"Meterial Stock Solution","label_zt":"庫存材料轉用處理方案說明","data_type":"text","reference_itemname":null},{"name":"cn_old_project_number","label":"Old Project","label_zt":"舊專案代號","data_type":"string","reference_itemname":null},{"name":"cn_project_number","label":"Project Number","label_zt":"專案代號","data_type":"foreign","reference_itemname":null},{"name":"cn_rd_dept_head","label":"RD Dept. Head","label_zt":"RD Dept. Head","data_type":"item","reference_itemname":"Identity"},{"name":"cn_reason_code","label":"Reason Code","label_zt":"變更原因代碼","data_type":"list","reference_itemname":"Reason Code"},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"description","label":"Change Description","label_zt":"描述","data_type":"text","reference_itemname":null},{"name":"item_number","label":"Number","label_zt":"EN 編號","data_type":"sequence","reference_itemname":null},{"name":"jpc_hasvnpart","label":"Check VN","label_zt":"檢查VN料號","data_type":"boolean","reference_itemname":null},{"name":"jpc_message_vn_part","label":"Check VN part number","label_zt":"VN料號","data_type":"text","reference_itemname":null},{"name":"jpc_other_factory_noti","label":"Notifty Other Factory","label_zt":"其他廠區通知","data_type":"list","reference_itemname":"Part_Factory"},{"name":"jpc_trans_finished","label":"","label_zt":"是否已拋轉","data_type":"integer","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"發起者","data_type":"item","reference_itemname":"Identity"},{"name":"priority","label":"Priority","label_zt":"緊急程度","data_type":"list","reference_itemname":"Express Change Priorities"},{"name":"project","label":"Project","label_zt":"專案","data_type":"item","reference_itemname":"Project"},{"name":"rd_dept_manager","label":"RD Dept. Manager","label_zt":"RD Dept. Manager","data_type":"item","reference_itemname":"Identity"},{"name":"release_date","label":"Release Date","label_zt":"生效日期","data_type":"date","reference_itemname":null},{"name":"state","label":"Status","label_zt":"表單狀態","data_type":"string","reference_itemname":null},{"name":"title","label":"Title","label_zt":"主旨","data_type":"text","reference_itemname":null}]},{"name":"JPC RFQ","label":"RFQ/S/D","label_zt":"RFQ/S/D","properties":[{"name":"classification","label":"Classification","label_zt":"類別","data_type":"string","reference_itemname":null},{"name":"cn_factory","label":"Factory","label_zt":"負責廠別","data_type":"list","reference_itemname":"Part_Factory"},{"name":"created_by_id","label":"Creator","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Create Date","label_zt":"申請日期","data_type":"date","reference_itemname":null},{"name":"item_number","label":"RFQ/S/D Number","label_zt":"RFQ/S/D 編號","data_type":"string","reference_itemname":null},{"name":"jpc_cad","label":"Report - CAD","label_zt":"工作回報-圖號","data_type":"item","reference_itemname":"CAD"},{"name":"jpc_cost","label":"Report - Cost","label_zt":"工作回報-成本","data_type":"item","reference_itemname":"File"},{"name":"jpc_cost_unit","label":"RFQ-Unit Cost (USD)","label_zt":"RFQ單價成本(USD)","data_type":"float","reference_itemname":null},{"name":"jpc_cust_part","label":"Report-Customer Part","label_zt":"工作回報-客戶料號","data_type":"string","reference_itemname":null},{"name":"jpc_customer","label":"Customer","label_zt":"客戶","data_type":"foreign","reference_itemname":null},{"name":"jpc_epb_part","label":"Report-EPB P/N","label_zt":"工作回報-EPB料號","data_type":"string","reference_itemname":null},{"name":"jpc_expect_date","label":"Expect Finished Date","label_zt":"預計完成日期","data_type":"date","reference_itemname":null},{"name":"jpc_has_file","label":"Has file?","label_zt":"是否有附件","data_type":"boolean","reference_itemname":null},{"name":"jpc_hours","label":"Hours","label_zt":"總工時","data_type":"float","reference_itemname":null},{"name":"jpc_is_action_todo","label":"Is Todo","label_zt":"是否執行","data_type":"boolean","reference_itemname":null},{"name":"jpc_is_purchase","label":"Is outsouring or planning","label_zt":"是否(外購/評估中)不建立料號","data_type":"boolean","reference_itemname":null},{"name":"jpc_part","label":"Report-Part","label_zt":"工作回報-料號","data_type":"item","reference_itemname":"Part"},{"name":"jpc_part_link_cad","label":"Has Part link CAD","label_zt":"是否料號連結圖面","data_type":"boolean","reference_itemname":null},{"name":"jpc_proj_id","label":"Project","label_zt":"專案代號","data_type":"item","reference_itemname":"Project"},{"name":"jpc_proj_state","label":"Is MP?","label_zt":"是否專案量產","data_type":"list","reference_itemname":"RFQSD_Proj_Link"},{"name":"jpc_require_date","label":"*Required Date End","label_zt":"*需求到期日(必填)","data_type":"date","reference_itemname":null},{"name":"jpc_rfq_note","label":"*RFQ Name","label_zt":"*產品料號(必填)","data_type":"string","reference_itemname":null},{"name":"jpc_rfq_note2","label":"*Product Description","label_zt":"*規格描述(必填)","data_type":"string","reference_itemname":null},{"name":"jpc_standard_env","label":"*Standard Enviroment","label_zt":"*環保要求(必填)","data_type":"list","reference_itemname":"Part_StandardEnviroment"},{"name":"jpc_state_label","label":"Form State","label_zt":"表單狀態","data_type":"foreign","reference_itemname":null},{"name":"managed_by_id","label":"Manager","label_zt":"工程主管","data_type":"item","reference_itemname":"Identity"},{"name":"owned_by_id","label":"Owner","label_zt":"負責工程師","data_type":"item","reference_itemname":"Identity"},{"name":"state","label":"State","label_zt":"狀態","data_type":"string","reference_itemname":null}]},{"name":"Part","label":"Part","label_zt":"零組件","properties":[{"name":"bcs_autonumber","label":"Number","label_zt":"正式料號","data_type":"string","reference_itemname":null},{"name":"bcs_ref_current_state_label","label":"State","label_zt":"狀態","data_type":"foreign","reference_itemname":null},{"name":"classification","label":"Classification","label_zt":"料件子類別","data_type":"string","reference_itemname":null},{"name":"cn_announcement_type","label":"Announcement Type","label_zt":"公告大類","data_type":"list","reference_itemname":"Part_AnnouncementType"},{"name":"cn_awg","label":"Awg","label_zt":"AWG(可複選)","data_type":"mv_list","reference_itemname":null},{"name":"cn_cable_be_used","label":"Cable Be Used","label_zt":"用途","data_type":"list","reference_itemname":"Part_Cablebeused"},{"name":"cn_cable_type","label":"Cable Type","label_zt":"Cable Type(可複選)","data_type":"mv_list","reference_itemname":null},{"name":"cn_color","label":"Color","label_zt":"Color","data_type":"list","reference_itemname":"Part_Color"},{"name":"cn_component_type","label":"Component Type","label_zt":"料件類型(製造/外包/虛擬/採購)","data_type":"list","reference_itemname":"Part_ComponentsTypes"},{"name":"cn_factory","label":"Factory","label_zt":"建立廠別","data_type":"list","reference_itemname":"Part_Factory"},{"name":"cn_labor_standard_cost","label":"Labor Standard Cost(USD)","label_zt":"人工標準成本(USD)","data_type":"float","reference_itemname":null},{"name":"cn_lifecycle","label":"Lifecycle Phase","label_zt":"Lifecycle Phase","data_type":"list","reference_itemname":"Part_LifecyclePhase"},{"name":"cn_material_standard_cost","label":"Material Standard Cost(USD)","label_zt":"材料標準成本(USD)","data_type":"float","reference_itemname":null},{"name":"cn_manufacture_standard_cost","label":"Manufacture Standard Cost(USD)","label_zt":"製費標準成本(USD)","data_type":"float","reference_itemname":null},{"name":"cn_old_part_number","label":"Old Part Number","label_zt":"舊料號","data_type":"string","reference_itemname":null},{"name":"cn_old_project_id","label":"Old Project Code","label_zt":"舊專案代號","data_type":"item","reference_itemname":"Old Project"},{"name":"cn_outsourcing_standard_cost","label":"Outsourcing Standard Cost(USD)","label_zt":"外包標準成本(USD)","data_type":"float","reference_itemname":null},{"name":"cn_part_note","label":"Notes","label_zt":"料號備註","data_type":"string","reference_itemname":null},{"name":"cn_product_lines","label":"Product Line(s)","label_zt":"Product Line(s)","data_type":"mv_list","reference_itemname":null},{"name":"cn_revision","label":"Revision","label_zt":"Revision","data_type":"string","reference_itemname":null},{"name":"cn_standard_enviroment","label":"Standard Enviroment","label_zt":"環保標準","data_type":"list","reference_itemname":"Part_StandardEnviroment"},{"name":"cn_supplier","label":"Supplier","label_zt":"外購件供應商","data_type":"item","reference_itemname":"Vendor"},{"name":"cn_supplier_part","label":"Supplier Part Number","label_zt":"供應商料號","data_type":"string","reference_itemname":null},{"name":"cn_weight","label":"Unit Weight","label_zt":"單位重量(g)","data_type":"float","reference_itemname":null},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"has_change_pending","label":"Changes","label_zt":"變更中","data_type":"boolean","reference_itemname":null},{"name":"item_number","label":"Part Number","label_zt":"零組件料號","data_type":"string","reference_itemname":null},{"name":"jpc_bom_released_date","label":"EN/ECN First Add Change Released","label_zt":"EN/ECN 最初申請日(只有新增)","data_type":"date","reference_itemname":null},{"name":"jpc_chkbom_gc","label":"Check BOM GC-HF Error","label_zt":"檢查BOM是否GC-HF異常","data_type":"boolean","reference_itemname":null},{"name":"jpc_first_change_actual_creator","label":"EN/ECN First Actual Creator","label_zt":"EN/ECN 最初實際申請者","data_type":"item","reference_itemname":"Identity"},{"name":"jpc_first_change_date","label":"EN/ECN First Created On","label_zt":"EN/ECN 最初申請日(含變更)","data_type":"date","reference_itemname":null},{"name":"jpc_first_change_owner","label":"EN/ECN First Create Owner","label_zt":"EN/ECN 最初發起者","data_type":"item","reference_itemname":"Identity"},{"name":"jpc_last_change_date","label":"EN/ECN Last Released Date","label_zt":"EN/ECN 最後發行日","data_type":"date","reference_itemname":null},{"name":"jpc_notice_customer","label":"Change Notice","label_zt":"變更通知客戶","data_type":"item","reference_itemname":"NotiChanges"},{"name":"jpc_part_class1","label":"Category 1","label_zt":"產品大類","data_type":"list","reference_itemname":"Part_Class1"},{"name":"jpc_part_class2","label":"Category 2","label_zt":"產品中類","data_type":"list","reference_itemname":"Part_Class2"},{"name":"jpc_part_class3","label":"Category 3","label_zt":"產品小類","data_type":"list","reference_itemname":"Part_Class3"},{"name":"name","label":"Description","label_zt":"品名及規格","data_type":"string","reference_itemname":null},{"name":"name_2","label":"Customer Description","label_zt":"客戶品名描述","data_type":"string","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"擁有者","data_type":"item","reference_itemname":"Identity"},{"name":"project","label":"Project","label_zt":"專案","data_type":"item","reference_itemname":"Project"},{"name":"release_date","label":"Release Date","label_zt":"料號發行日期","data_type":"date","reference_itemname":null},{"name":"unit","label":"Unit","label_zt":"單位","data_type":"list","reference_itemname":"Units"}]},{"name":"Project","label":"Project","label_zt":"專案","properties":[{"name":"auto_create_dco","label":"自動檢查與建立文件EN","label_zt":"自動檢查與建立文件EN","data_type":"boolean","reference_itemname":null},{"name":"bcs_ref_current_state_label","label":"State","label_zt":"狀態","data_type":"foreign","reference_itemname":null},{"name":"cn_currency","label":"Currency","label_zt":"幣別","data_type":"list","reference_itemname":"cn_currency"},{"name":"cn_customer_code","label":"Customer Code","label_zt":"Customer Code","data_type":"string","reference_itemname":null},{"name":"cn_depcode","label":"Dep Code(C、T)","label_zt":"Dep Code(C、T)","data_type":"list","reference_itemname":"cn_project_dep_code"},{"name":"cn_extend_model","label":"Model","label_zt":"原生/衍生機種","data_type":"list","reference_itemname":"cn_project_model"},{"name":"cn_old_proj","label":"Old Project","label_zt":"舊專案代號","data_type":"item","reference_itemname":"Old Project"},{"name":"cn_part","label":"Product Number","label_zt":"成品料號","data_type":"item","reference_itemname":"Part"},{"name":"cn_product_type","label":"Product Type","label_zt":"產品別","data_type":"filter list","reference_itemname":null},{"name":"cn_project_number","label":"Project Number","label_zt":"專案編號","data_type":"string","reference_itemname":null},{"name":"cn_total_pm_maintain_cost","label":"Total Cost","label_zt":"預估總投資費用(原幣)","data_type":"float","reference_itemname":null},{"name":"comments","label":"Comments","label_zt":"備註","data_type":"text","reference_itemname":null},{"name":"created_by_id","label":"Created By","label_zt":"建立者","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"customer","label":"customer","label_zt":"客戶","data_type":"item","reference_itemname":"Customer"},{"name":"date_due_act","label":"Act Finish","label_zt":"實際完成日期","data_type":"date","reference_itemname":null},{"name":"date_due_sched","label":"Sched Due","label_zt":"預計完成時間","data_type":"date","reference_itemname":null},{"name":"date_start_act","label":"Act Start","label_zt":"實際開始日期","data_type":"date","reference_itemname":null},{"name":"date_start_sched","label":"Sched Start","label_zt":"預計起始時間","data_type":"date","reference_itemname":null},{"name":"from_template","label":"From Template","label_zt":"來自範本","data_type":"item","reference_itemname":"Project Template"},{"name":"is_plan_type","label":"","label_zt":"專案表別","data_type":"list","reference_itemname":"IS_PLAN_TYPE"},{"name":"jpc_buyrq_cost","label":"BuyRQ Total Cost NTD","label_zt":"EPB總費用合計NTD","data_type":"string","reference_itemname":null},{"name":"jpc_proj_buy_onreview","label":"APR Cost In Review","label_zt":"APR總費用合計(申請中)","data_type":"string","reference_itemname":null},{"name":"jpc_proj_old","label":"總費用合計2022版","label_zt":"總費用合計2022版","data_type":"string","reference_itemname":null},{"name":"name","label":"Name","label_zt":"專案名稱","data_type":"string","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"專案負責人","data_type":"item","reference_itemname":"Identity"},{"name":"project_number","label":"System Number","label_zt":"系統流水碼","data_type":"integer","reference_itemname":null},{"name":"scheduling_mode","label":"Scheduling Mode","label_zt":"排程規則","data_type":"list","reference_itemname":"PM_scheduling_modes"},{"name":"state","label":"Status","label_zt":"狀態","data_type":"string","reference_itemname":null}]},{"name":"Simple ECO","label":"CA","label_zt":"CA零件承認簽審單","properties":[{"name":"bcs_afterchange","label":"afterChange","label_zt":"變更後描述","data_type":"formatted text","reference_itemname":null},{"name":"bcs_beforechange","label":"beforeChange","label_zt":"變更前描述","data_type":"formatted text","reference_itemname":null},{"name":"bcs_isrestricted","label":"isrestricted","label_zt":"專案專屬","data_type":"boolean","reference_itemname":null},{"name":"bcs_ref_current_state_label","label":"State","label_zt":"狀態","data_type":"foreign","reference_itemname":null},{"name":"change_category","label":"Change Category","label_zt":"變更種類","data_type":"list","reference_itemname":"Change Categories"},{"name":"change_reason","label":"Note","label_zt":"備註","data_type":"text","reference_itemname":null},{"name":"classification","label":"Classification","label_zt":"分類","data_type":"string","reference_itemname":null},{"name":"cn_check","label":"Check","label_zt":"Check","data_type":"item","reference_itemname":"Identity"},{"name":"cn_dept","label":"Creator Dept","label_zt":"製表單位","data_type":"item","reference_itemname":"Identity"},{"name":"cn_error_note","label":"","label_zt":"提示訊息","data_type":"text","reference_itemname":null},{"name":"cn_factory","label":"Factory","label_zt":"廠區","data_type":"list","reference_itemname":"Part_Factory"},{"name":"cn_rd_head","label":"RD Dept. Head","label_zt":"RD Dept. Head","data_type":"item","reference_itemname":"Identity"},{"name":"created_by_id","label":"Creator","label_zt":"建立人員","data_type":"item","reference_itemname":"User"},{"name":"created_on","label":"Created On","label_zt":"建立日期","data_type":"date","reference_itemname":null},{"name":"description","label":"Description","label_zt":"名稱描述","data_type":"text","reference_itemname":null},{"name":"item_number","label":"CA Number","label_zt":"CA編號","data_type":"sequence","reference_itemname":null},{"name":"jpc_trans_finished","label":"","label_zt":"是否已拋轉","data_type":"integer","reference_itemname":null},{"name":"owned_by_id","label":"Owned By","label_zt":"發起者","data_type":"item","reference_itemname":"Identity"},{"name":"rd_dept_manager","label":"RD Dept. Manager","label_zt":"RD Dept. Manager","data_type":"item","reference_itemname":"Identity"},{"name":"release_date","label":"Release Date","label_zt":"發行日期","data_type":"date","reference_itemname":null},{"name":"state","label":"Status","label_zt":"狀態","data_type":"string","reference_itemname":null},{"name":"title","label":"","label_zt":"title","data_type":"text","reference_itemname":null}]}]}
        """  # Truncated for readability
        
        resources.append(
            Resource(
            uri="mssql://schema_info",
            name="Database Schema Information",
            mimeType="application/json",
            description="Detailed schema information for database tables:"+schema_info,
            )
        )
        # Add SQL query help resources
        resources.append(
            Resource(
                uri="mssql://query_examples",
                name="SQL Query Examples",
                mimeType="text/plain",
                description="Common SQL query examples and best practices"
            )
        )

        # Add resource to emphasize filtering with is_current=1
        resources.append(
            Resource(
            uri="mssql://best_practices/is_current",
            name="Current Records Filter",
            mimeType="text/plain",
            description="IMPORTANT: Always use WHERE is_current=1 when querying Part, CAD, and Document tables to get only current/active records and avoid retrieving historical versions"
            )
        )

        resources.append(
            Resource(
                uri="mssql://relationship_queries",
                name="Relationship Queries",
                mimeType="text/plain",
                description="How to query relationships between tables"
            )
        )

        return resources
    except Exception as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Aras System Read table contents."""
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")
    
    if not uri_str.startswith("mssql://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")
        
    parts = uri_str[8:].split('/')
    table = parts[0]
    
    try:
        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        # Use TOP 100 for MSSQL (equivalent to LIMIT in MySQL)
        cursor.execute(f"SELECT TOP 100 * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [",".join(map(str, row)) for row in rows]
        cursor.close()
        conn.close()
        return "\n".join([",".join(columns)] + result)
                
    except Exception as e:
        logger.error(f"Database error reading resource {uri}: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Aras System List available SQL Server tools."""
    logger.info("Listing tools...")
    return [
        Tool(
            name="execute_sql",
            description="Aras SQL Execute an SQL query on the SQL Server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Aras System Execute SQL commands."""
    config = get_db_config()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")
    
    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")
    
    try:
        conn = pymssql.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)
        logger.info(f"Executing SQL: {query}")
        # Special handling for table listing
        if query.strip().upper().startswith("SELECT") and "INFORMATION_SCHEMA.TABLES" in query.upper():
            tables = cursor.fetchall()
            result = ["Tables_in_" + config["database"]]  # Header
            result.extend([table[0] for table in tables])
            cursor.close()
            conn.close()
            return [TextContent(type="text", text="\n".join(result))]
        
        # Regular SELECT queries
        elif query.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            def safe_str(val):
                logger.info(val)
                return str(val).encode('utf-8', errors='ignore').decode('utf-8') if val is not None else ''
            result = [",".join(map(safe_str, row)) for row in rows]
            cursor.close()
            conn.close()
            logger.info(f"Query result: {result}")
            return [TextContent(type="text", text="\n".join([",".join(columns)] + result))]
        
        # Block non-SELECT queries
        else:
            cursor.close()
            conn.close()
            raise ValueError("Only SELECT queries are allowed for security reasons")
                
    except Exception as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]

async def main():
    """Aras System Main entry point to run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting MSSQL MCP server...")
    try:
        # 驗證資料庫連線，但不要在主線程中引發異常
        config = get_db_config()
        logger.info(f"Database config: {config['server']}/{config['database']} as {config['user']}")
        
        # 測試資料庫連線
        try:
            conn = pymssql.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            logger.info("成功連線到資料庫")
        except Exception as db_e:
            logger.error(f"資料庫連線測試失敗: {str(db_e)}")
            logger.error("伺服器將繼續執行，但資料庫操作可能會失敗")
            # 記錄詳細錯誤信息在標準錯誤輸出
            print(f"資料庫連線測試失敗: {str(db_e)}", file=sys.stderr)
            print(f"請確認資料庫連線設定是否正確", file=sys.stderr)
        
        async with stdio_server() as (read_stream, write_stream):
            try:
                await app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options()
                )
            except Exception as e:
                logger.error(f"Server error: {str(e)}", exc_info=True)
                # 記錄詳細錯誤信息在標準錯誤輸出
                print(f"MCP 伺服器執行時發生錯誤: {str(e)}", file=sys.stderr)
                # 不重新拋出異常，讓程式繼續運行
                # 等待一段時間，以便錯誤訊息被讀取
                await asyncio.sleep(1)
    except Exception as main_e:
        # 捕獲所有主函數可能遇到的異常
        error_msg = f"主函數執行發生錯誤: {str(main_e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg, file=sys.stderr)
        # 等待一段時間，以便錯誤訊息被讀取
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
