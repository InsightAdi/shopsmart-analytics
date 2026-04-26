import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Step 1 — Check if .env loaded
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    print("   Make sure .env exists in the same folder as this script")
else:
    print("✅ Step 1 — Connection string loaded from .env")
    
    # Step 2 — Show URL structure (password hidden)
    try:
        # Mask password for safe printing
        parts = DATABASE_URL.split("@")
        before_at = parts[0]  # postgresql://postgres:PASSWORD
        after_at  = parts[1]  # host:port/dbname
        
        creds = before_at.split(":")
        masked = creds[0] + ":" + creds[1] + ":****@" + after_at
        print(f"✅ Step 2 — URL structure: {masked}")
        
        # Check port
        if "6543" in after_at:
            print("❌ ERROR: You are using port 6543 (Transaction Pooler)")
            print("   You need port 5432 (Direct Connection)")
            print("   Go to Supabase → Settings → Database → Connection string")
            print("   Select 'Direct connection' and copy that URL")
        elif "5432" in after_at:
            print("✅ Step 3 — Port 5432 confirmed (Direct Connection)")
        else:
            print("⚠️  WARNING: Could not detect port number in URL")
            
    except Exception as e:
        print(f"⚠️  Could not parse URL structure: {e}")

# Step 3 — Attempt actual connection using psycopg2 directly
print("\n--- Attempting database connection ---\n")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get PostgreSQL version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ CONNECTED SUCCESSFULLY!")
    print(f"   PostgreSQL: {version[:60]}")
    
    # Check tables
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    table_count = cursor.fetchone()[0]
    print(f"   Tables in database: {table_count}")
    
    cursor.close()
    conn.close()
    print("\n🎉 Everything looks great — ready for Phase 4!")

except psycopg2.OperationalError as e:
    error_msg = str(e)
    print(f"❌ Connection FAILED")
    print(f"   Error: {error_msg}")
    print()
    
    # Specific diagnoses
    if "password authentication failed" in error_msg:
        print("🔍 DIAGNOSIS: Wrong password")
        print("   → Reset password in Supabase → Project Settings → Database")
        
    elif "Tenant or user not found" in error_msg:
        print("🔍 DIAGNOSIS: Wrong connection string type")
        print("   → You are using the Pooler URL, not the Direct URL")
        print("   → In Supabase go to: Settings → Database → Connection string")
        print("   → Look for a toggle that says 'Direct connection'")
        print("   → Copy THAT URL (it will have db.xxxx.supabase.co in it)")
        
    elif "could not translate host name" in error_msg:
        print("🔍 DIAGNOSIS: Hostname not found — check your project ref in the URL")
        
    elif "SSL" in error_msg:
        print("🔍 DIAGNOSIS: SSL issue")
        print("   → Add ?sslmode=require at the end of your DATABASE_URL")
        
    else:
        print("🔍 DIAGNOSIS: Unknown error — paste the full error above for help")

except Exception as e:
    print(f"❌ Unexpected error: {type(e).__name__}: {e}")