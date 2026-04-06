"""Google Sheets tools — read, write, create spreadsheets, format cells."""

import json
from auth import get_service


def _sheets():
    return get_service("sheets", "v4")


def sheets_read(spreadsheet_id: str, range: str = "Sheet1") -> str:
    """Read values from a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        range: A1 notation range (e.g. 'Sheet1!A1:D10', 'Sheet1', 'A1:C5').
    """
    svc = _sheets()
    result = svc.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    return json.dumps({
        "range": result.get("range", ""),
        "values": result.get("values", []),
    }, indent=2)


def sheets_write(spreadsheet_id: str, range: str, values: list[list]) -> str:
    """Write values to a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        range: A1 notation range to write to (e.g. 'Sheet1!A1').
        values: 2D array of values to write (e.g. [['Name', 'Age'], ['Alice', 30]]).
    """
    svc = _sheets()
    result = svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range,
        valueInputOption="USER_ENTERED",
        body={"values": values}
    ).execute()
    return json.dumps({
        "status": "written",
        "updatedRange": result.get("updatedRange", ""),
        "updatedCells": result.get("updatedCells", 0),
    })


def sheets_append(spreadsheet_id: str, range: str, values: list[list]) -> str:
    """Append rows to a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        range: A1 notation range to append after (e.g. 'Sheet1!A1').
        values: 2D array of rows to append.
    """
    svc = _sheets()
    result = svc.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range,
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": values}
    ).execute()
    updates = result.get("updates", {})
    return json.dumps({
        "status": "appended",
        "updatedRange": updates.get("updatedRange", ""),
        "updatedRows": updates.get("updatedRows", 0),
    })


def sheets_create(title: str, sheet_names: list[str] = None) -> str:
    """Create a new Google Spreadsheet.

    Args:
        title: Spreadsheet title.
        sheet_names: List of sheet/tab names to create (default: ['Sheet1']).
    """
    svc = _sheets()
    sheets = [{"properties": {"title": name}} for name in (sheet_names or ["Sheet1"])]
    result = svc.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": sheets
    }).execute()
    return json.dumps({
        "status": "created",
        "spreadsheetId": result["spreadsheetId"],
        "url": result.get("spreadsheetUrl", ""),
        "sheets": [s["properties"]["title"] for s in result.get("sheets", [])]
    })


def sheets_clear(spreadsheet_id: str, range: str) -> str:
    """Clear values from a range in a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        range: A1 notation range to clear (e.g. 'Sheet1!A1:D10').
    """
    svc = _sheets()
    svc.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range, body={}).execute()
    return json.dumps({"status": "cleared", "range": range})


def sheets_get_info(spreadsheet_id: str) -> str:
    """Get metadata about a spreadsheet (title, sheets, etc).

    Args:
        spreadsheet_id: The spreadsheet ID.
    """
    svc = _sheets()
    result = svc.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = [{"title": s["properties"]["title"], "sheetId": s["properties"]["sheetId"],
               "rowCount": s["properties"]["gridProperties"]["rowCount"],
               "columnCount": s["properties"]["gridProperties"]["columnCount"]}
              for s in result.get("sheets", [])]
    return json.dumps({
        "title": result["properties"]["title"],
        "spreadsheetId": result["spreadsheetId"],
        "url": result.get("spreadsheetUrl", ""),
        "sheets": sheets
    }, indent=2)


def sheets_batch_update(spreadsheet_id: str, data: list[dict]) -> str:
    """Write to multiple ranges in a single request.

    Args:
        spreadsheet_id: The spreadsheet ID.
        data: List of dicts, each with 'range' (A1 notation) and 'values' (2D array).
              Example: [{"range": "Sheet1!A1", "values": [["a","b"]]}, {"range": "Sheet2!A1", "values": [[1,2]]}]
    """
    svc = _sheets()
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [{"range": d["range"], "values": d["values"]} for d in data],
    }
    result = svc.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    return json.dumps({
        "status": "batch_written",
        "totalUpdatedCells": result.get("totalUpdatedCells", 0),
        "totalUpdatedRows": result.get("totalUpdatedRows", 0),
    })


def sheets_add_sheet(spreadsheet_id: str, title: str) -> str:
    """Add a new sheet/tab to a spreadsheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        title: Name for the new sheet.
    """
    svc = _sheets()
    result = svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{"addSheet": {"properties": {"title": title}}}]
    }).execute()
    props = result["replies"][0]["addSheet"]["properties"]
    return json.dumps({"status": "sheet_added", "sheetId": props["sheetId"], "title": props["title"]})


def sheets_delete_sheet(spreadsheet_id: str, sheet_id: int) -> str:
    """Delete a sheet/tab from a spreadsheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        sheet_id: The numeric sheet ID (from sheets_get_info, NOT the sheet name).
    """
    svc = _sheets()
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{"deleteSheet": {"sheetId": sheet_id}}]
    }).execute()
    return json.dumps({"status": "sheet_deleted", "sheetId": sheet_id})


def sheets_merge_cells(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                       start_col: int, end_col: int, merge_type: str = "MERGE_ALL") -> str:
    """Merge cells in a sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        sheet_id: The numeric sheet ID.
        start_row: Start row index (0-based).
        end_row: End row index (exclusive).
        start_col: Start column index (0-based).
        end_col: End column index (exclusive).
        merge_type: 'MERGE_ALL', 'MERGE_COLUMNS', or 'MERGE_ROWS'.
    """
    svc = _sheets()
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{
            "mergeCells": {
                "range": {"sheetId": sheet_id, "startRowIndex": start_row, "endRowIndex": end_row,
                          "startColumnIndex": start_col, "endColumnIndex": end_col},
                "mergeType": merge_type,
            }
        }]
    }).execute()
    return json.dumps({"status": "cells_merged"})


def sheets_add_chart(spreadsheet_id: str, sheet_id: int, chart_type: str,
                     data_range: str, title: str = "") -> str:
    """Add a basic chart to a sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        sheet_id: The numeric sheet ID.
        chart_type: Chart type — 'BAR', 'LINE', 'AREA', 'COLUMN', 'SCATTER', 'COMBO', 'STEPPED_AREA'.
        data_range: A1 notation of the data range (e.g. 'Sheet1!A1:B10').
        title: Chart title.
    """
    svc = _sheets()
    # Parse range into GridRange
    from googleapiclient.errors import HttpError
    spec = {
        "title": title,
        "basicChart": {
            "chartType": chart_type,
            "legendPosition": "BOTTOM_LEGEND",
            "axis": [
                {"position": "BOTTOM_AXIS"},
                {"position": "LEFT_AXIS"},
            ],
            "domains": [{"domain": {"sourceRange": {"sources": [
                {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 100,
                 "startColumnIndex": 0, "endColumnIndex": 1}
            ]}}}],
            "series": [{"series": {"sourceRange": {"sources": [
                {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 100,
                 "startColumnIndex": 1, "endColumnIndex": 2}
            ]}}, "targetAxis": "LEFT_AXIS"}],
        }
    }
    result = svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{
            "addChart": {
                "chart": {
                    "spec": spec,
                    "position": {"overlayPosition": {"anchorCell": {
                        "sheetId": sheet_id, "rowIndex": 0, "columnIndex": 3
                    }}}
                }
            }
        }]
    }).execute()
    chart_id = result["replies"][0]["addChart"]["chart"]["chartId"]
    return json.dumps({"status": "chart_added", "chartId": chart_id})


def sheets_add_conditional_format(spreadsheet_id: str, sheet_id: int,
                                  start_row: int, end_row: int,
                                  start_col: int, end_col: int,
                                  rule_type: str, values: list[str],
                                  bg_color: str = "#FF0000") -> str:
    """Add conditional formatting to a range.

    Args:
        spreadsheet_id: The spreadsheet ID.
        sheet_id: The numeric sheet ID.
        start_row: Start row index (0-based).
        end_row: End row index (exclusive).
        start_col: Start column index (0-based).
        end_col: End column index (exclusive).
        rule_type: Condition type — 'NUMBER_GREATER', 'NUMBER_LESS', 'TEXT_CONTAINS',
                   'TEXT_NOT_CONTAINS', 'CUSTOM_FORMULA', 'NUMBER_BETWEEN', 'BLANK', 'NOT_BLANK'.
        values: Condition values (e.g. ['100'] for NUMBER_GREATER, or ['=A1>B1'] for CUSTOM_FORMULA).
        bg_color: Background color hex (e.g. '#FF0000' for red).
    """
    svc = _sheets()
    r = int(bg_color[1:3], 16) / 255
    g = int(bg_color[3:5], 16) / 255
    b = int(bg_color[5:7], 16) / 255

    condition_values = [{"userEnteredValue": v} for v in values]
    svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{"sheetId": sheet_id, "startRowIndex": start_row, "endRowIndex": end_row,
                                "startColumnIndex": start_col, "endColumnIndex": end_col}],
                    "booleanRule": {
                        "condition": {"type": rule_type, "values": condition_values},
                        "format": {"backgroundColor": {"red": r, "green": g, "blue": b}},
                    }
                },
                "index": 0,
            }
        }]
    }).execute()
    return json.dumps({"status": "conditional_format_added"})


def sheets_add_named_range(spreadsheet_id: str, name: str, sheet_id: int,
                           start_row: int, end_row: int,
                           start_col: int, end_col: int) -> str:
    """Create a named range in a spreadsheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        name: Name for the range (e.g. 'SalesData').
        sheet_id: The numeric sheet ID.
        start_row: Start row index (0-based).
        end_row: End row index (exclusive).
        start_col: Start column index (0-based).
        end_col: End column index (exclusive).
    """
    svc = _sheets()
    result = svc.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": [{
            "addNamedRange": {
                "namedRange": {
                    "name": name,
                    "range": {"sheetId": sheet_id, "startRowIndex": start_row, "endRowIndex": end_row,
                              "startColumnIndex": start_col, "endColumnIndex": end_col},
                }
            }
        }]
    }).execute()
    nr_id = result["replies"][0]["addNamedRange"]["namedRange"]["namedRangeId"]
    return json.dumps({"status": "named_range_added", "namedRangeId": nr_id, "name": name})
