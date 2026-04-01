# test_mark_read.py
from gmail_service import GmailService
import os

def main():
    os.chdir(os.path.dirname(__file__))  # ensure working dir is project root
    svc = GmailService()                 # runs auth if needed

    # Print the authenticated user's email (sanity)
    try:
        profile = svc.service.users().getProfile(userId='me').execute()
        print("Authenticated as:", profile.get('emailAddress'))
    except Exception as e:
        print("Could not fetch profile:", e)

    emails = svc.get_unread_emails(max_results=1)
    print("Fetched unread emails:", emails)

    if not emails:
        print("No unread emails found (API returned empty list).")
        return

    mid = emails[0]['id']
    before = svc.get_message_labels(mid)
    print("Labels BEFORE modify:", before)

    ok = svc.mark_as_read(mid)
    print("mark_as_read returned:", ok)

    after = svc.get_message_labels(mid)
    print("Labels AFTER modify:", after)

if __name__ == "__main__":
    main()
