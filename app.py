from flask import Flask, render_template, request, redirect, url_for
from database.db_manager import (
    DBManager, ProgramManager, DisciplinesManager, ProfessionsManager,
    PracticeManager, GraduatesManager, ContactManager, BudgetPlacesManager,
    MinScoresManager, PassingScoresManager
)
from comparison import ComparisonManager

comparison_manager = ComparisonManager()
app = Flask(__name__)

GRADUATE_DB_PATH = 'database/graduate_programs.db'
UNDERGRADUATE_DB_PATH = 'database/undergraduate_programs.db'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        level = request.form.get('level')
        return redirect(url_for('programs', level=level, accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'
    css_file = 'css/accessible.css' if accessible else 'css/style.css'
    return render_template('index.html', css_file=css_file, accessible=accessible)


@app.route('/programs/<level>', methods=['GET', 'POST'])
def programs(level):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)
    disciplines_manager = DisciplinesManager(db_manager, level)

    filters = {}
    unique_disciplines = disciplines_manager.get_all_unique()
    unique_durations = []

    if request.method == 'POST':
        min_passing_score = request.form.get('min_passing_score', '')
        duration = request.form.get('duration', '')
        min_budget_places = request.form.get('min_budget_places', '')
        discipline = request.form.get('discipline', '')

        if min_passing_score:
            filters['min_passing_score'] = int(min_passing_score)
        if duration:
            filters['duration'] = duration
        if min_budget_places:
            filters['min_budget_places'] = int(min_budget_places)
        if discipline:
            filters['discipline'] = discipline

    programs_list = program_manager.select_many(filters)
    enriched_programs = []

    for program in programs_list:
        program_id = program['id']
        passing_score = program_manager.get_passing_score(program_id)
        budget_places = program_manager.get_budget_places(program_id)
        duration = program.get('study_duration', program.get('duration', '-'))
        if duration and duration not in unique_durations:
            unique_durations.append(duration)
        enriched_programs.append({
            'id': program_id,
            'name': program['name'],
            'duration': duration,
            'passing_score': passing_score if passing_score else '-',
            'budget_places': budget_places if budget_places else '-'
        })

    return render_template(
        'programs.html',
        programs=enriched_programs,
        level=level,
        unique_disciplines=unique_disciplines,
        unique_durations=unique_durations,
        filters=filters,
        accessible=accessible
    )


@app.route('/program/<level>/<int:program_id>')
def program_detail(level, program_id):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)
    disciplines_manager = DisciplinesManager(db_manager, level)
    professions_manager = ProfessionsManager(db_manager, level)
    practice_manager = PracticeManager(db_manager, level)
    graduates_manager = GraduatesManager(db_manager, level)
    contact_manager = ContactManager(db_manager, level)
    budget_places_manager = BudgetPlacesManager(db_manager, level)
    min_scores_manager = MinScoresManager(db_manager, level)
    passing_scores_manager = PassingScoresManager(db_manager, level)

    program = program_manager.select_one(program_id)
    if not program:
        return redirect(url_for('programs', level=level, accessible=request.args.get('accessible')))

    program_details = {
        'id': program['id'],
        'name': program['name'],
        'level': program['level'],
        'code': program['code'],
        'specialty_type': program['specialty_type'],
        'study_form': program.get('study_form', program.get('form', '-')),
        'duration': program.get('study_duration', program.get('duration', '-')),
        'language': program['language'],
        'tuition_fee': program['tuition_fee'],
        'disciplines': disciplines_manager.select_by_program(program_id),
        'professions': professions_manager.select_by_program(program_id),
        'practices': practice_manager.select_by_program(program_id),
        'graduates': graduates_manager.select_by_program(program_id),
        'contacts': contact_manager.select_by_program(program_id),
        'budget_places': budget_places_manager.select_by_program(
            program_id) if level == 'undergraduate' else program.get('budget_places', 0),
        'paid_places': program.get('paid_places', program.get('total_paid_places', 0)),
        'min_scores': min_scores_manager.select_by_program(program_id) if level == 'undergraduate' else [],
        'passing_scores': passing_scores_manager.select_by_program(program_id) if level == 'undergraduate' else []
    }

    return render_template('program_detail.html', program=program_details, level=level, accessible=accessible)


@app.route('/add_to_comparison/<level>/<int:program_id>', methods=['POST'])
def add_to_comparison(level, program_id):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)

    comparison_manager.add_program(level, program_id, program_manager)
    return redirect(url_for('programs', level=level, accessible='true' if accessible else 'false'))


@app.route('/remove_from_comparison/<level>/<int:program_id>', methods=['POST'])
def remove_from_comparison(level, program_id):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    comparison_manager.remove_program(level, program_id)
    return redirect(url_for('compare', level=level, accessible='true' if accessible else 'false'))


@app.route('/compare/<level>')
def compare(level):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)

    comparison_data = comparison_manager.compare_programs(level, program_manager)
    return render_template('compare.html', comparison_data=comparison_data, level=level, accessible=accessible)


@app.route('/program_details/<level>/<int:program_id>')
def program_details(level, program_id):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)

    program_data = comparison_manager.get_detailed_info(level, program_id, program_manager)
    return render_template('program_details.html', program=program_data, level=level, accessible=accessible)


@app.route('/filter/<level>')
def filter_page(level):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    # Здесь у тебя было redirect на programs — добавим accessible
    return redirect(url_for('programs', level=level, accessible='true' if accessible else 'false'))


@app.route('/final/<level>')
def final_page(level):
    if level not in ['graduate', 'undergraduate']:
        return redirect(url_for('index', accessible=request.args.get('accessible')))
    accessible = request.args.get('accessible') == 'true'

    db_path = GRADUATE_DB_PATH if level == 'graduate' else UNDERGRADUATE_DB_PATH
    db_manager = DBManager(db_path)
    program_manager = ProgramManager(db_manager, level)

    comparison_data = comparison_manager.compare_programs(level, program_manager)
    return render_template('final.html', level=level, comparison_data=comparison_data, accessible=accessible)


if __name__ == '__main__':
    app.run(debug=True)