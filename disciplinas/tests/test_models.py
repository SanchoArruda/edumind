from django.test import TestCase

from disciplinas.models import Disciplina


class DisciplinaModelTest(TestCase):

    def test_deve_criar_disciplina_com_nome(self):
        disciplina = Disciplina.objects.create(nome="Banco de Dados")

        self.assertEqual(disciplina.nome, "Banco de Dados")
        self.assertEqual(str(disciplina), "Banco de Dados")

    def test_deve_ordenar_disciplinas_por_nome(self):
        Disciplina.objects.create(nome="Redes")
        Disciplina.objects.create(nome="Algoritmos")
        Disciplina.objects.create(nome="Banco de Dados")

        disciplinas = list(Disciplina.objects.all())

        self.assertEqual(disciplinas[0].nome, "Algoritmos")
        self.assertEqual(disciplinas[1].nome, "Banco de Dados")
        self.assertEqual(disciplinas[2].nome, "Redes")

    def test_verbose_name_deve_ser_disciplina(self):
        self.assertEqual(Disciplina._meta.verbose_name, "Disciplina")

    def test_verbose_name_plural_deve_ser_disciplinas(self):
        self.assertEqual(Disciplina._meta.verbose_name_plural, "Disciplinas")