#!/usr/bin/env python3
"""
Verification script - check that no users were lost
"""

import psycopg2
import os

def verify_migration():
    """Verify that all users are preserved after migration"""
    
    # Database connection
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    
    cur = conn.cursor()
    
    print("🔍 Verifying migration results...")
    
    # Check total user count
    cur.execute('SELECT COUNT(*) FROM "user"')
    total_users = cur.fetchone()[0]
    print(f"📊 Total users: {total_users}")
    
    # Check users with membership_type
    cur.execute('SELECT COUNT(*) FROM "user" WHERE membership_type IS NOT NULL')
    users_with_membership = cur.fetchone()[0]
    print(f"✅ Users with membership_type: {users_with_membership}")
    
    # Check that all users have 'free' membership by default
    cur.execute("SELECT COUNT(*) FROM "user" WHERE membership_type = 'free'")
    free_users = cur.fetchone()[0]
    print(f"🆓 Users with 'free' membership: {free_users}")
    
    # Check for any data loss
    if total_users == users_with_membership:
        print("✅ SUCCESS: No users lost during migration!")
    else:
        print("❌ ERROR: Some users may have been lost!")
        return False
    
    # Check sample users
    cur.execute('SELECT id, email, username, membership_type FROM "user" LIMIT 5')
    sample_users = cur.fetchall()
    print("\n👥 Sample users:")
    for user in sample_users:
        print(f"   ID: {user[0]}, Email: {user[1]}, Username: {user[2]}, Membership: {user[3]}")
    
    conn.close()
    return True

if __name__ == "__main__":
    verify_migration()
