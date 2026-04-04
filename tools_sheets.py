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
