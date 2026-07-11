"""tests/conftest.py — pytest ortak ayarları (turkgram).

Paket editable kurulu (`pip install -e .`) olduğundan `import turkgram` her yerden
çalışır. `pythonpath = ["."]` (pyproject) `tests` paketini de yola ekler, böylece
`from tests.golden_verbs import GOLDEN` çözülür. DB/dış bağımlılık YOK — motor saf.
"""
