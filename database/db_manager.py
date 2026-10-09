# import sqlite3
# from typing import List, Dict, Any

# class DBManager:
#     def __init__(self, db_path: str):
#         self.db_path = db_path

#     def get_connection(self):
#         return sqlite3.connect(self.db_path)

#     def execute_query(self, query: str, params: tuple = ()) -> None:
#         conn = self.get_connection()
#         cursor = conn.cursor()
#         cursor.execute(query, params)
#         conn.commit()
#         conn.close()

#     def fetch_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
#         conn = self.get_connection()
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#         cursor.execute(query, params)
#         rows = cursor.fetchall()
#         result = [dict(row) for row in rows]
#         conn.close()
#         return result


# class ProgramManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level  # 'graduate' or 'undergraduate'
#         self.table_name = 'Program' if level == 'graduate' else 'programs'

#     def insert(self, data: Dict[str, Any]) -> None:
#         keys = ', '.join(data.keys())
#         placeholders = ', '.join(['?' for _ in data])
#         query = f"INSERT INTO {self.table_name} ({keys}) VALUES ({placeholders})"
#         self.db_manager.execute_query(query, tuple(data.values()))

#     def update(self, program_id: int, data: Dict[str, Any]) -> None:
#         updates = ', '.join([f"{key} = ?" for key in data.keys()])
#         query = f"UPDATE {self.table_name} SET {updates} WHERE id = ?"
#         self.db_manager.execute_query(query, tuple(data.values()) + (program_id,))

#     def select_one(self, program_id: int) -> Dict[str, Any]:
#         query = f"SELECT * FROM {self.table_name} WHERE id = ?"
#         result = self.db_manager.fetch_query(query, (program_id,))
#         return result[0] if result else {}

#     def select_many(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
#         query = f"SELECT * FROM {self.table_name}"
#         params = []
#         joins = []
#         conditions = []

#         if filters:
#             if 'min_passing_score' in filters and filters['min_passing_score'] and self.level == 'undergraduate':
#                 joins.append(f"JOIN passing_scores ps ON {self.table_name}.id = ps.program_id")
#                 conditions.append("ps.score >= ?")
#                 params.append(filters['min_passing_score'])

#             if 'duration' in filters and filters['duration']:
#                 duration_field = 'study_duration' if self.level == 'graduate' else 'duration'
#                 conditions.append(f"{self.table_name}.{duration_field} = ?")
#                 params.append(filters['duration'])

#             if 'min_budget_places' in filters and filters['min_budget_places']:
#                 if self.level == 'undergraduate':
#                     joins.append(f"""
#                         JOIN (
#                             SELECT program_id, SUM(places) as total_places
#                             FROM budget_places
#                             GROUP BY program_id
#                         ) bp ON {self.table_name}.id = bp.program_id
#                     """)
#                     conditions.append("bp.total_places >= ?")
#                     params.append(filters['min_budget_places'])
#                 else:
#                     conditions.append(f"{self.table_name}.budget_places >= ?")
#                     params.append(filters['min_budget_places'])

#             if 'discipline' in filters and filters['discipline']:
#                 discipline_table = 'Disciplines' if self.level == 'graduate' else 'disciplines'
#                 discipline_field = 'discipline_name' if self.level == 'graduate' else 'discipline'
#                 joins.append(f"JOIN {discipline_table} d ON {self.table_name}.id = d.program_id")
#                 conditions.append(f"d.{discipline_field} = ?")
#                 params.append(filters['discipline'])

#             if joins or conditions:
#                 if joins:
#                     query = f"SELECT DISTINCT {self.table_name}.* FROM {self.table_name} " + " ".join(joins)
#                 if conditions:
#                     query += " WHERE " + " AND ".join(conditions)

#         print("Query:", query)  # Для отладки
#         print("Params:", params)  # Для отладки
#         return self.db_manager.fetch_query(query, tuple(params))

#     def delete(self, program_id: int) -> None:
#         query = f"DELETE FROM {self.table_name} WHERE id = ?"
#         self.db_manager.execute_query(query, (program_id,))

#     def get_passing_score(self, program_id: int) -> int:
#         if self.level == 'undergraduate':
#             query = "SELECT score FROM passing_scores WHERE program_id = ? ORDER BY year DESC LIMIT 1"
#             result = self.db_manager.fetch_query(query, (program_id,))
#             return result[0]['score'] if result else 0
#         return 0  # Для магистратуры данных о проходных баллах нет

#     def get_budget_places(self, program_id: int) -> int:
#         if self.level == 'undergraduate':
#             query = "SELECT SUM(places) as total FROM budget_places WHERE program_id = ?"
#             result = self.db_manager.fetch_query(query, (program_id,))
#             return result[0]['total'] if result and result[0]['total'] else 0
#         else:
#             program = self.select_one(program_id)
#             return program.get('budget_places', 0)

#     def get_subjects(self, program_id: int) -> List[str]:
#         if self.level == 'undergraduate':
#             query = "SELECT subject FROM min_scores WHERE program_id = ?"
#             result = self.db_manager.fetch_query(query, (program_id,))
#             return [row['subject'] for row in result]
#         return []


# class DisciplinesManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'Disciplines' if level == 'graduate' else 'disciplines'
#         self.field_name = 'discipline_name' if level == 'graduate' else 'discipline'

#     def select_by_program(self, program_id: int) -> List[str]:
#         query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
#         result = self.db_manager.fetch_query(query, (program_id,))
#         return [row[self.field_name] for row in result]

#     def get_all_unique(self) -> List[str]:
#         query = f"SELECT DISTINCT {self.field_name} FROM {self.table_name}"
#         result = self.db_manager.fetch_query(query)
#         return [row[self.field_name] for row in result]


# class ProfessionsManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'Professions' if level == 'graduate' else 'professions'
#         self.field_name = 'profession_name' if level == 'graduate' else 'profession'

#     def select_by_program(self, program_id: int) -> List[str]:
#         query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
#         result = self.db_manager.fetch_query(query, (program_id,))
#         return [row[self.field_name] for row in result]


# class PracticeManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'Practice' if level == 'graduate' else 'practice_places'
#         self.field_name = 'practice_name' if level == 'graduate' else 'place'

#     def select_by_program(self, program_id: int) -> List[str]:
#         query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
#         result = self.db_manager.fetch_query(query, (program_id,))
#         return [row[self.field_name] for row in result]

# class GraduatesManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'Graduates' if level == 'graduate' else 'graduates'
#         self.field_name = 'graduate_info' if level == 'graduate' else 'info'

#     def select_by_program(self, program_id: int) -> List[str]:
#         query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
#         result = self.db_manager.fetch_query(query, (program_id,))
#         return [row[self.field_name] for row in result]


# class ContactManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'Contacts' if level == 'graduate' else 'contacts'

#     def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
#         query = f"SELECT * FROM {self.table_name} WHERE program_id = ?"
#         return self.db_manager.fetch_query(query, (program_id,))


# class BudgetPlacesManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'budget_places'

#     def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
#         if self.level == 'undergraduate':
#             query = f"SELECT year, places FROM {self.table_name} WHERE program_id = ?"
#             return self.db_manager.fetch_query(query, (program_id,))
#         return []


# class MinScoresManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'min_scores'

#     def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
#         if self.level == 'undergraduate':
#             query = f"SELECT subject, score FROM {self.table_name} WHERE program_id = ?"
#             return self.db_manager.fetch_query(query, (program_id,))
#         return []


# class PassingScoresManager:
#     def __init__(self, db_manager: DBManager, level: str):
#         self.db_manager = db_manager
#         self.level = level
#         self.table_name = 'passing_scores'

#     def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
#         if self.level == 'undergraduate':
#             query = f"SELECT year, score FROM {self.table_name} WHERE program_id = ? ORDER BY year DESC"
#             return self.db_manager.fetch_query(query, (program_id,))
#         return []

import sqlite3
from typing import List, Dict, Any

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = ()) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result


class ProgramManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level  # 'graduate' or 'undergraduate'
        self.table_name = 'Program' if level == 'graduate' else 'programs'

    def insert(self, data: Dict[str, Any]) -> None:
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {self.table_name} ({keys}) VALUES ({placeholders})"
        self.db_manager.execute_query(query, tuple(data.values()))

    def update(self, program_id: int, data: Dict[str, Any]) -> None:
        updates = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {self.table_name} SET {updates} WHERE id = ?"
        self.db_manager.execute_query(query, tuple(data.values()) + (program_id,))

    def select_one(self, program_id: int) -> Dict[str, Any]:
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        result = self.db_manager.fetch_query(query, (program_id,))
        return result[0] if result else {}

    def select_many(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table_name}"
        params = []
        joins = []
        conditions = []

        if filters:
            if 'min_passing_score' in filters and filters['min_passing_score'] and self.level == 'undergraduate':
                joins.append(f"JOIN passing_scores ps ON {self.table_name}.id = ps.program_id")
                conditions.append("ps.score >= ?")
                params.append(filters['min_passing_score'])

            if 'duration' in filters and filters['duration']:
                duration_field = 'study_duration' if self.level == 'graduate' else 'duration'
                conditions.append(f"{self.table_name}.{duration_field} = ?")
                params.append(filters['duration'])

            if 'min_budget_places' in filters and filters['min_budget_places']:
                if self.level == 'undergraduate':
                    joins.append(f"""
                        JOIN (
                            SELECT program_id, SUM(places) as total_places
                            FROM budget_places
                            GROUP BY program_id
                        ) bp ON {self.table_name}.id = bp.program_id
                    """)
                    conditions.append("bp.total_places >= ?")
                    params.append(filters['min_budget_places'])
                else:
                    conditions.append(f"{self.table_name}.budget_places >= ?")
                    params.append(filters['min_budget_places'])

            if 'discipline' in filters and filters['discipline']:
                discipline_table = 'Disciplines' if self.level == 'graduate' else 'disciplines'
                discipline_field = 'discipline_name' if self.level == 'graduate' else 'discipline'
                joins.append(f"JOIN {discipline_table} d ON {self.table_name}.id = d.program_id")
                conditions.append(f"d.{discipline_field} = ?")
                params.append(filters['discipline'])

            if joins or conditions:
                if joins:
                    query = f"SELECT DISTINCT {self.table_name}.* FROM {self.table_name} " + " ".join(joins)
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

        return self.db_manager.fetch_query(query, tuple(params))

    def delete(self, program_id: int) -> None:
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self.db_manager.execute_query(query, (program_id,))

    def get_passing_score(self, program_id: int) -> int:
        if self.level == 'undergraduate':
            query = "SELECT score FROM passing_scores WHERE program_id = ? ORDER BY year DESC LIMIT 1"
            result = self.db_manager.fetch_query(query, (program_id,))
            return result[0]['score'] if result else 0
        return 0  # Для магистратуры данных о проходных баллах может не быть

    def get_budget_places(self, program_id: int) -> int:
        if self.level == 'undergraduate':
            query = "SELECT SUM(places) as total FROM budget_places WHERE program_id = ?"
            result = self.db_manager.fetch_query(query, (program_id,))
            return result[0]['total'] if result and result[0]['total'] else 0
        else:
            program = self.select_one(program_id)
            return program.get('budget_places', 0)

    def get_subjects(self, program_id: int) -> List[str]:
        if self.level == 'undergraduate':
            query = "SELECT subject FROM min_scores WHERE program_id = ?"
            result = self.db_manager.fetch_query(query, (program_id,))
            return [row['subject'] for row in result]
        return []


class DisciplinesManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level
        self.table_name = 'Disciplines' if level == 'graduate' else 'disciplines'
        self.field_name = 'discipline_name' if level == 'graduate' else 'discipline'

    def select_by_program(self, program_id: int) -> List[str]:
        query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
        result = self.db_manager.fetch_query(query, (program_id,))
        return [row[self.field_name] for row in result]

    def get_all_unique(self) -> List[str]:
        query = f"SELECT DISTINCT {self.field_name} FROM {self.table_name}"
        result = self.db_manager.fetch_query(query)
        return [row[self.field_name] for row in result]


class ProfessionsManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level
        self.table_name = 'Professions' if level == 'graduate' else 'professions'
        self.field_name = 'profession_name' if level == 'graduate' else 'profession'

    def select_by_program(self, program_id: int) -> List[str]:
        query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
        result = self.db_manager.fetch_query(query, (program_id,))
        return [row[self.field_name] for row in result]


class PracticeManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level
        self.table_name = 'Practice' if level == 'graduate' else 'practice_places'
        self.field_name = 'practice_name' if level == 'graduate' else 'place'

    def select_by_program(self, program_id: int) -> List[str]:
        query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
        result = self.db_manager.fetch_query(query, (program_id,))
        return [row[self.field_name] for row in result]


class GraduatesManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level
        self.table_name = 'Graduates' if level == 'graduate' else 'employment_orgs'
        self.field_name = 'graduate_org' if level == 'graduate' else 'org'

    def select_by_program(self, program_id: int) -> List[str]:
        query = f"SELECT {self.field_name} FROM {self.table_name} WHERE program_id = ?"
        result = self.db_manager.fetch_query(query, (program_id,))
        return [row[self.field_name] for row in result]


class ContactManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level
        self.table_name = 'Contact' if level == 'graduate' else 'contacts'

    def select_by_program(self, program_id: int) -> List[Dict[str, str]]:
        query = f"SELECT contact_name, contact_email FROM {self.table_name} WHERE program_id = ?"
        return self.db_manager.fetch_query(query, (program_id,))


class BudgetPlacesManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level

    def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
        if self.level == 'undergraduate':
            query = "SELECT quota_type, places FROM budget_places WHERE program_id = ?"
            return self.db_manager.fetch_query(query, (program_id,))
        else:
            return []


class MinScoresManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level

    def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
        if self.level == 'undergraduate':
            query = "SELECT subject, score, is_mandatory FROM min_scores WHERE program_id = ?"
            return self.db_manager.fetch_query(query, (program_id,))
        else:
            return []


class PassingScoresManager:
    def __init__(self, db_manager: DBManager, level: str):
        self.db_manager = db_manager
        self.level = level

    def select_by_program(self, program_id: int) -> List[Dict[str, Any]]:
        if self.level == 'undergraduate':
            query = "SELECT year, score FROM passing_scores WHERE program_id = ? ORDER BY year DESC"
            return self.db_manager.fetch_query(query, (program_id,))
        else:
            return []