"""Google Contacts (People API) tools — search, list, create, update, delete contacts."""

import json
from auth import get_service


def _people():
    return get_service("people", "v1")


PERSON_FIELDS = "names,emailAddresses,phoneNumbers,organizations,addresses,biographies"


def contacts_search(query: str, max_results: int = 20) -> str:
    """Search contacts by name, email, or phone number.

    Args:
        query: Search query (name, email, or phone number).
        max_results: Maximum contacts to return.
    """
    svc = _people()
    result = svc.people().searchContacts(
        query=query, readMask=PERSON_FIELDS, pageSize=max_results
    ).execute()

    contacts = []
    for r in result.get("results", []):
        person = r.get("person", {})
        contacts.append(_format_person(person))
    return json.dumps(contacts, indent=2) if contacts else "No contacts found."


def contacts_list(max_results: int = 50) -> str:
    """List all contacts.

    Args:
        max_results: Maximum contacts to return.
    """
    svc = _people()
    result = svc.people().connections().list(
        resourceName="people/me", personFields=PERSON_FIELDS, pageSize=max_results,
        sortOrder="LAST_NAME_ASCENDING"
    ).execute()

    contacts = [_format_person(p) for p in result.get("connections", [])]
    return json.dumps(contacts, indent=2) if contacts else "No contacts found."


def contacts_create(given_name: str, family_name: str = "", email: str = "",
                    phone: str = "", organization: str = "", title: str = "") -> str:
    """Create a new contact.

    Args:
        given_name: First name.
        family_name: Last name.
        email: Email address.
        phone: Phone number.
        organization: Company/organization name.
        title: Job title.
    """
    svc = _people()
    person = {"names": [{"givenName": given_name, "familyName": family_name}]}

    if email:
        person["emailAddresses"] = [{"value": email}]
    if phone:
        person["phoneNumbers"] = [{"value": phone}]
    if organization or title:
        person["organizations"] = [{"name": organization, "title": title}]

    result = svc.people().createContact(body=person).execute()
    return json.dumps({"status": "created", "resourceName": result["resourceName"],
                       "name": f"{given_name} {family_name}".strip()})


def contacts_update(resource_name: str, given_name: str = "", family_name: str = "",
                    email: str = "", phone: str = "", organization: str = "",
                    title: str = "") -> str:
    """Update an existing contact.

    Args:
        resource_name: Contact resource name (e.g. 'people/c123456').
        given_name: New first name (empty = no change).
        family_name: New last name (empty = no change).
        email: New email (empty = no change).
        phone: New phone (empty = no change).
        organization: New organization (empty = no change).
        title: New job title (empty = no change).
    """
    svc = _people()
    # Get current contact with etag
    current = svc.people().get(resourceName=resource_name, personFields=PERSON_FIELDS).execute()

    update_fields = []
    if given_name or family_name:
        current["names"] = [{"givenName": given_name or current.get("names", [{}])[0].get("givenName", ""),
                             "familyName": family_name or current.get("names", [{}])[0].get("familyName", "")}]
        update_fields.append("names")
    if email:
        current["emailAddresses"] = [{"value": email}]
        update_fields.append("emailAddresses")
    if phone:
        current["phoneNumbers"] = [{"value": phone}]
        update_fields.append("phoneNumbers")
    if organization or title:
        current["organizations"] = [{"name": organization, "title": title}]
        update_fields.append("organizations")

    result = svc.people().updateContact(
        resourceName=resource_name, body=current,
        updatePersonFields=",".join(update_fields)
    ).execute()
    return json.dumps({"status": "updated", "resourceName": result["resourceName"]})


def contacts_delete(resource_name: str) -> str:
    """Delete a contact.

    Args:
        resource_name: Contact resource name (e.g. 'people/c123456').
    """
    svc = _people()
    svc.people().deleteContact(resourceName=resource_name).execute()
    return json.dumps({"status": "deleted", "resourceName": resource_name})


def contacts_list_groups(max_results: int = 50) -> str:
    """List all contact groups (labels).

    Args:
        max_results: Maximum groups to return.
    """
    svc = _people()
    result = svc.contactGroups().list(pageSize=max_results).execute()
    groups = []
    for g in result.get("contactGroups", []):
        groups.append({
            "resourceName": g.get("resourceName", ""),
            "name": g.get("name", ""),
            "formattedName": g.get("formattedName", ""),
            "groupType": g.get("groupType", ""),
            "memberCount": g.get("memberCount", 0),
        })
    return json.dumps(groups, indent=2)


def contacts_create_group(name: str) -> str:
    """Create a new contact group.

    Args:
        name: Name for the group.
    """
    svc = _people()
    result = svc.contactGroups().create(body={
        "contactGroup": {"name": name}
    }).execute()
    return json.dumps({"status": "created", "resourceName": result["resourceName"],
                       "name": result.get("name", "")})


def contacts_modify_group_members(group_resource_name: str,
                                  add_contacts: list[str] = None,
                                  remove_contacts: list[str] = None) -> str:
    """Add or remove contacts from a contact group.

    Args:
        group_resource_name: The group resource name (e.g. 'contactGroups/abc123').
        add_contacts: List of contact resource names to add (e.g. ['people/c123']).
        remove_contacts: List of contact resource names to remove.
    """
    svc = _people()
    body = {}
    if add_contacts:
        body["resourceNamesToAdd"] = add_contacts
    if remove_contacts:
        body["resourceNamesToRemove"] = remove_contacts

    svc.contactGroups().members().modify(
        resourceName=group_resource_name, body=body
    ).execute()
    return json.dumps({"status": "group_members_modified", "group": group_resource_name})


def contacts_batch_create(contacts: list[dict]) -> str:
    """Create multiple contacts in a single request.

    Args:
        contacts: List of contact dicts, each with keys: givenName, familyName, email, phone, organization, title.
                  Example: [{"givenName": "Alice", "email": "alice@co.com"}, {"givenName": "Bob"}]
    """
    svc = _people()
    contact_bodies = []
    for c in contacts:
        person = {"names": [{"givenName": c.get("givenName", ""), "familyName": c.get("familyName", "")}]}
        if c.get("email"):
            person["emailAddresses"] = [{"value": c["email"]}]
        if c.get("phone"):
            person["phoneNumbers"] = [{"value": c["phone"]}]
        if c.get("organization") or c.get("title"):
            person["organizations"] = [{"name": c.get("organization", ""), "title": c.get("title", "")}]
        contact_bodies.append({"contactPerson": person})

    result = svc.people().batchCreateContacts(body={"contacts": contact_bodies}).execute()
    created = []
    for entry in result.get("createdPeople", []):
        person = entry.get("person", {})
        created.append({
            "resourceName": person.get("resourceName", ""),
            "name": person.get("names", [{}])[0].get("displayName", ""),
        })
    return json.dumps({"status": "batch_created", "count": len(created), "contacts": created})


def contacts_batch_delete(resource_names: list[str]) -> str:
    """Delete multiple contacts in a single request.

    Args:
        resource_names: List of contact resource names to delete (e.g. ['people/c123', 'people/c456']).
    """
    svc = _people()
    svc.people().batchDeleteContacts(body={"resourceNames": resource_names}).execute()
    return json.dumps({"status": "batch_deleted", "count": len(resource_names)})


def contacts_get_photo(resource_name: str) -> str:
    """Get the URL of a contact's photo.

    Args:
        resource_name: Contact resource name (e.g. 'people/c123').
    """
    svc = _people()
    person = svc.people().get(resourceName=resource_name, personFields="photos").execute()
    photos = person.get("photos", [])
    if photos:
        return json.dumps({"resourceName": resource_name, "photoUrl": photos[0].get("url", ""),
                           "default": photos[0].get("default", False)})
    return json.dumps({"resourceName": resource_name, "photoUrl": "", "default": True})


def _format_person(person: dict) -> dict:
    """Format a Person resource into a clean dict."""
    names = person.get("names", [{}])
    name = names[0] if names else {}
    emails = [e["value"] for e in person.get("emailAddresses", [])]
    phones = [p["value"] for p in person.get("phoneNumbers", [])]
    orgs = person.get("organizations", [{}])
    org = orgs[0] if orgs else {}

    return {
        "resourceName": person.get("resourceName", ""),
        "name": name.get("displayName", f"{name.get('givenName', '')} {name.get('familyName', '')}".strip()),
        "emails": emails,
        "phones": phones,
        "organization": org.get("name", ""),
        "title": org.get("title", ""),
    }
