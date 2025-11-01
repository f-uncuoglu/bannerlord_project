from flask import Flask, render_template, request, jsonify
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    """Create a database connection"""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )

@app.route('/')
def index():
    """Home page"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get summary statistics
    cursor.execute("SELECT COUNT(*) as count FROM Troops")
    troop_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM Cultures")
    culture_count = cursor.fetchone()['count']
    
    # Get all cultures with troop counts
    cursor.execute("""
        SELECT c.culture_id, c.name, COUNT(t.troop_id) as troop_count
        FROM Cultures c
        LEFT JOIN Troops t ON c.culture_id = t.culture_id
        GROUP BY c.culture_id, c.name
        ORDER BY c.name
    """)
    cultures = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', 
                         troop_count=troop_count,
                         culture_count=culture_count,
                         cultures=cultures)

@app.route('/troops')
def troops():
    """List all troops"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get filter parameters
    culture_filter = request.args.get('culture', '')
    tier_filter = request.args.get('tier', '')
    mounted_filter = request.args.get('mounted', '')
    
    # Build query
    query = """
        SELECT t.*, c.name as culture_name
        FROM Troops t
        JOIN Cultures c ON t.culture_id = c.culture_id
        WHERE 1=1
    """
    params = []
    
    if culture_filter:
        query += " AND c.name = %s"
        params.append(culture_filter)
    
    if tier_filter:
        query += " AND t.tier = %s"
        params.append(int(tier_filter))
    
    if mounted_filter:
        query += " AND t.is_mounted = %s"
        params.append(1 if mounted_filter == 'yes' else 0)
    
    query += " ORDER BY c.name, t.tier, t.name"
    
    cursor.execute(query, params)
    troops_list = cursor.fetchall()
    
    # Get all cultures for filter dropdown
    cursor.execute("SELECT name FROM Cultures ORDER BY name")
    cultures = [row['name'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('troops.html', 
                         troops=troops_list,
                         cultures=cultures,
                         current_culture=culture_filter,
                         current_tier=tier_filter,
                         current_mounted=mounted_filter)

@app.route('/troop/<int:troop_id>')
def troop_detail(troop_id):
    """Detailed view of a single troop"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get troop info
    cursor.execute("""
        SELECT t.*, c.name as culture_name
        FROM Troops t
        JOIN Cultures c ON t.culture_id = c.culture_id
        WHERE t.troop_id = %s
    """, (troop_id,))
    troop = cursor.fetchone()
    
    if not troop:
        cursor.close()
        conn.close()
        return "Troop not found", 404
    
    # Get upgrade paths (what this troop can upgrade to)
    cursor.execute("""
        SELECT t.*, up.xp_cost
        FROM Troop_Upgrade_Paths up
        JOIN Troops t ON up.upgraded_troop_id = t.troop_id
        WHERE up.base_troop_id = %s
    """, (troop_id,))
    upgrades = cursor.fetchall()
    
    # Get prerequisite (what troop upgrades to this one)
    cursor.execute("""
        SELECT t.*, up.xp_cost
        FROM Troop_Upgrade_Paths up
        JOIN Troops t ON up.base_troop_id = t.troop_id
        WHERE up.upgraded_troop_id = %s
    """, (troop_id,))
    prerequisites = cursor.fetchall()
    
    # Get equipment for this troop
    cursor.execute("""
        SELECT tej.slot, i.name as item_name, i.item_id
        FROM Troop_Equipment_Junction tej
        JOIN Items i ON tej.item_id = i.item_id
        WHERE tej.troop_id = %s
        ORDER BY tej.slot
    """, (troop_id,))
    equipment_raw = cursor.fetchall()
    
    # Group equipment by slot
    equipment_by_slot = {}
    for item in equipment_raw:
        slot = item['slot']
        if slot not in equipment_by_slot:
            equipment_by_slot[slot] = []
        equipment_by_slot[slot].append(item)
    
    cursor.close()
    conn.close()
    
    return render_template('troop_detail.html',
                         troop=troop,
                         upgrades=upgrades,
                         prerequisites=prerequisites,
                         equipment=equipment_by_slot)

@app.route('/factions')
def factions():
    """List all factions/cultures"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, 
               COUNT(t.troop_id) as troop_count,
               AVG(t.wage) as avg_wage,
               SUM(t.is_mounted) as mounted_count
        FROM Cultures c
        LEFT JOIN Troops t ON c.culture_id = t.culture_id
        GROUP BY c.culture_id, c.name
        ORDER BY c.name
    """)
    cultures = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('factions.html', cultures=cultures)

@app.route('/faction/<int:culture_id>')
def faction_detail(culture_id):
    """Detailed view of a faction with its troops"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get culture info
    cursor.execute("SELECT * FROM Cultures WHERE culture_id = %s", (culture_id,))
    culture = cursor.fetchone()
    
    if not culture:
        cursor.close()
        conn.close()
        return "Faction not found", 404
    
    # Get all troops for this culture, organized by tier
    cursor.execute("""
        SELECT * FROM Troops
        WHERE culture_id = %s
        ORDER BY tier, name
    """, (culture_id,))
    troops = cursor.fetchall()
    
    # Organize by tier
    troops_by_tier = {}
    for troop in troops:
        tier = troop['tier']
        if tier not in troops_by_tier:
            troops_by_tier[tier] = []
        troops_by_tier[tier].append(troop)
    
    cursor.close()
    conn.close()
    
    return render_template('faction_detail.html',
                         culture=culture,
                         troops_by_tier=troops_by_tier)

@app.route('/api/troops')
def api_troops():
    """API endpoint to get troops as JSON"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT t.*, c.name as culture_name
        FROM Troops t
        JOIN Cultures c ON t.culture_id = c.culture_id
        ORDER BY t.name
    """)
    troops = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(troops)

if __name__ == '__main__':
    app.run(debug=True)