import datetime
import threading
import customtkinter as ctk
from tkinter import filedialog
from sqlitedict import SqliteDict
import pandas as pd
import re
import keyboard
from PIL import Image
import numpy


class DataHandler:
    @staticmethod
    def save(key, value, cache_file="cache.sqlite3"):
        try:
            with SqliteDict(cache_file) as mydict:
                mydict[key] = value
                mydict.commit()
        except Exception as ex:
            print(f"Erro durante o armazenamento de dados: {ex}")

    @staticmethod
    def load(key, cache_file="cache.sqlite3"):
        try:
            with SqliteDict(cache_file) as mydict:
                value = mydict[key]
            return value
        except Exception as ex:
            print(f"Erro durante o carregamento de dados: {ex}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Registro veicular")
        self.geometry("800x650")
        self.resizable(width=False, height=False)

        keyboard.add_hotkey('ctrl+f1', self.select_directory)

        self.img_back = ctk.CTkImage(Image.open("assets/icons/icons8-back-ios-17-glyph/icons8-back-30.png"),
                                     size=(30, 30))

        self.adesivo = Adesivo()
        self.input_adesivo = ctk.StringVar()

        self.btn_back_to_search = ctk.CTkButton(self, text="Voltar", image=self.img_back, command=self.back_to_search,
                                                fg_color='transparent')
        self.btn_att_anual = ctk.CTkButton(self, text='Atualizar Anual', height=38)
        self.define_label = ctk.CTkLabel(self, text='Definir como:')

        self.header_frame = HeaderFrame(master=self, fg_color='#1A55B1', corner_radius=0).pack(fill=ctk.X, expand=False,
                                                                                               side=ctk.TOP)
        self.search_frame = SearchFrame(master=self, fg_color='transparent')
        self.search_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.information_frame = InformationFrame(master=self, width=350, height=150)

        self.status_label = ctk.CTkLabel(self.search_frame, text='Adesivo não encontrado.\n Deseja cadastrar ?')
        self.btn_register = ctk.CTkButton(self.search_frame, text='Cadastrar', fg_color='transparent')

        ctk.CTkLabel(self, text='Desenvolvido por S2 Luiz Gabriel - V0.1').pack(fill=ctk.X, expand=False,
                                                                                side=ctk.BOTTOM)

    def search_adesivo(self):
        if len(self.input_adesivo.get()) >= 4:

            path_sheet = DataHandler.load("url_sheet")
            if path_sheet:
                self.status_label.grid_forget()
                self.btn_register.grid_forget()
                df = pd.read_excel(path_sheet)

                df.set_index("ADESIVO", inplace=True)

                try:
                    result = df.loc[self.input_adesivo.get(), :]

                    print(result)
                    if not result.empty:
                        pessoal = Pessoal()
                        pessoal.set(posto=result['POSTO/GRAD'], nome_guerra=result['NOME DE GUERRA'],
                                    nome_completo=result['NOME COMPLETO'],
                                    saram=int(result["SARAM"]) if not numpy.isnan(
                                        result["SARAM"]) else "", contato=result['RAMAL'], setor=result['SETOR'],
                                    om=result['OM'], habilitacao=result['HABILITAÇÃO'],
                                    val_habilitacao=result['VALIDADE HAB.'])

                        veiculo = Veiculo()
                        veiculo.set(placa=result['PLACA'], marca=result['MARCA'], modelo=result['MODELO'],
                                    cor=result['COR'], ano_veiculo=result['ANO VEÍCULO'])
                        status_att = result['STATUS']
                        today = datetime.date.today()
                        current_year = today.year

                        self.btn_back_to_search.place(y=-75, x=80, rely=1, anchor=ctk.SW)


                        if status_att != 'DEVOLVIDO' and status_att != 'EXTRAVIADO':
                            if result['ANO'] == current_year:
                                status_att = 'ATUALIZADO'
                            else:
                                status_att = 'DESATUALIZADO'
                                self.btn_att_anual.place(y=-75, x=(80 + self.btn_back_to_search.winfo_width()) + 30, rely=1, anchor=ctk.SW)
                        self.adesivo.set(adesivo=self.input_adesivo.get(), status=status_att, ano=result['ANO'],
                                         pessoal=pessoal, veiculo=veiculo)

                        self.input_adesivo.set("")

                        self.define_label.place(y=-80, x=(self.btn_att_anual.winfo_width() + (80 + self.btn_back_to_search.winfo_width()) + 30) + 30, rely=1, anchor=ctk.SW)

                        self.information_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

                        self.search_frame.place_forget()


                except Exception as ex:
                    print('Erro na pesquisa do adesivo - ' + str(ex))
                    self.status_label.grid(row=3, column=0, padx=10)
                    self.btn_register.grid(row=4, column=0, padx=(10, 10))

    def search_adesivo_threaded(self):
        thread = threading.Thread(target=self.search_adesivo)
        thread.start()

    def select_directory(self):
        sheet_path = filedialog.askopenfilename(filetypes=(("Sheet", (".ods", ".xlsx")), ("All Files", "*.*")))
        DataHandler.save("url_sheet", sheet_path)

    def back_to_search(self):
        self.information_frame.place_forget()
        self.btn_back_to_search.place_forget()
        self.search_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)


class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        font_label_CCSO = ctk.CTkFont(family="roboto", size=20)

        (ctk.CTkLabel(self, text='Célula de Contrainteligência e Segurança Orgânica', font=font_label_CCSO)
         .grid(row=0, column=0, padx=10, sticky='w'))

        ctk.CTkLabel(self, text='Força Aérea Brasileira').grid(row=1, column=0, padx=10, sticky='w')


class SearchFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        font_entry_adesivo = ctk.CTkFont(family="roboto", size=20)

        validate_entry_adesivo = (
            self.register(lambda number: re.match("^[0-9]*$", number) is not None and len(number) <= 5), "%P"
        )

        ctk.CTkLabel(self, text="Adesivo").grid(row=0, column=0, padx=10, pady=1, sticky="w")
        ctk.CTkEntry(
            self, justify="center", font=font_entry_adesivo, width=150, height=40,
            validate="key", textvariable=master.input_adesivo, validatecommand=validate_entry_adesivo
        ).grid(row=1, column=0, padx=10, pady=(0, 10))
        ctk.CTkButton(
            self, text="Continuar", command=master.search_adesivo_threaded
        ).grid(row=2, column=0, padx=10, pady=(0, 10), sticky="snew")


class InformationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text='Informações', fg_color="gray30",
                     corner_radius=5).grid(row=0,
                                           column=0,
                                           padx=10,
                                           pady=(10, 0),
                                           sticky="nsew",
                                           columnspan=4)
        ctk.CTkLabel(self, text='Número do Adesivo').grid(row=1, column=0, padx=10, pady=1)
        ctk.CTkLabel(self, text='Adesivo Anual').grid(row=1, column=1, padx=10, pady=1)
        ctk.CTkLabel(self, text='Status').grid(row=1, column=2, padx=10, pady=1)
        ctk.CTkCheckBox(self, text='Devolvido').grid(row=1, column=3)
        ctk.CTkCheckBox(self, text='Extraviado').grid(row=2, column=3)

        ctk.CTkLabel(self, textvariable=master.adesivo.id).grid(row=2, column=0, padx=10, pady=1)
        ctk.CTkLabel(self, textvariable=master.adesivo.ano).grid(row=2, column=1, padx=10, pady=1)
        ctk.CTkLabel(self, textvariable=master.adesivo.status).grid(row=2, column=2, padx=10, pady=1)

        ctk.CTkLabel(self, text="Pessoal", fg_color="gray30", width=550,
                     corner_radius=5).grid(row=3,
                                           column=0,
                                           padx=10,
                                           pady=(10, 0),
                                           sticky="nsew",
                                           columnspan=4)
        ctk.CTkLabel(self, text="Posto").grid(row=4, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Nome de Guerra").grid(row=4, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Nome Completo").grid(row=4, column=2, pady=1, padx=10, columnspan=2)
        ctk.CTkLabel(self, text="Organização Militar").grid(row=6, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Setor").grid(row=6, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Saram").grid(row=6, column=2, pady=1, padx=10)
        ctk.CTkLabel(self, text="Contato").grid(row=6, column=3, pady=1, padx=10)

        ctk.CTkOptionMenu(self,
                          values=['S2', 'S1', 'CB', '3S', '2S', '1S', 'SO', 'AP', '2T', '1T', 'CP', 'MJ', 'TC', 'CL',
                                  'BG', 'T2', 'T1', 'CV'], variable=master.adesivo.pessoal.posto, anchor='center',
                          fg_color='#4c4b4b', button_color='#3d3c3c').grid(row=5, column=0, padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.pessoal.nome_guerra, justify='center', border_width=0,
                     fg_color='transparent').grid(row=5, column=1, padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.pessoal.nome_completo, justify='center', border_width=0,
                     fg_color='transparent', width=300).grid(row=5, column=2, padx=10, columnspan=2)

        ctk.CTkOptionMenu(self,
                          values=['GSD-RF', 'BARF', 'CINDACTA III', 'SEREP-RF', 'II COMAR', 'GAP-RF', 'HARF', 'OARF',
                                  'PARF', 'PTTC', 'SERIPA II', 'CBMPE'], variable=master.adesivo.pessoal.om,
                          anchor='center', fg_color='#4c4b4b', button_color='#3d3c3c').grid(row=7, column=0, padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.pessoal.setor, justify='center', border_width=0,
                     fg_color='transparent').grid(row=7, column=1, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.pessoal.saram, justify='center', border_width=0,
                     fg_color='transparent').grid(row=7, column=2, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.pessoal.contato, justify='center', border_width=0,
                     fg_color='transparent').grid(row=7, column=3, pady=(0, 3), padx=10)

        ctk.CTkLabel(self, text="Veiculo", fg_color="gray30", width=550,
                     corner_radius=5).grid(row=8,
                                           column=0,
                                           padx=10,
                                           pady=(
                                               10, 0),
                                           sticky="nsew",
                                           columnspan=4)
        ctk.CTkLabel(self, text="Placa").grid(row=9, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Marca").grid(row=9, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Modelo").grid(row=9, column=2, pady=1, padx=10)
        ctk.CTkLabel(self, text="Cor").grid(row=9, column=3, pady=1, padx=10)
        ctk.CTkLabel(self, text="Ano").grid(row=11, column=0, pady=1, padx=10)

        ctk.CTkEntry(self, textvariable=master.adesivo.veiculo.placa, justify='center', border_width=0,
                     fg_color='transparent').grid(row=10, column=0, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.veiculo.marca, justify='center', border_width=0,
                     fg_color='transparent').grid(row=10, column=1, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.veiculo.modelo, justify='center', border_width=0,
                     fg_color='transparent').grid(row=10, column=2, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.veiculo.cor, justify='center', border_width=0,
                     fg_color='transparent').grid(row=10, column=3, pady=(0, 3), padx=10)
        ctk.CTkEntry(self, textvariable=master.adesivo.veiculo.ano_veiculo, justify='center', border_width=0,
                     fg_color='transparent').grid(row=12, column=0, pady=(0, 3), padx=10)


class Pessoal:
    def __init__(self):
        self.posto = ctk.StringVar()
        self.nome_guerra = ctk.StringVar()
        self.nome_completo = ctk.StringVar()
        self.setor = ctk.StringVar()
        self.om = ctk.StringVar()
        self.contato = ctk.StringVar()
        self.saram = ctk.StringVar()
        self.habilitacao = ctk.StringVar()
        self.val_habilitacao = ctk.StringVar()

    def set(self, posto, nome_guerra, nome_completo, saram, contato, setor, om, habilitacao, val_habilitacao):
        self.posto.set(posto)
        self.nome_guerra.set(nome_guerra)
        self.nome_completo.set(nome_completo)
        self.setor.set(setor)
        self.om.set(om)
        self.contato.set(contato)
        self.saram.set(saram)
        self.habilitacao.set(habilitacao)
        self.val_habilitacao.set(val_habilitacao)


class Veiculo:
    def __init__(self):
        self.placa = ctk.StringVar()
        self.cor = ctk.StringVar()
        self.marca = ctk.StringVar()
        self.modelo = ctk.StringVar()
        self.ano_veiculo = ctk.StringVar()

    def set(self, placa, marca, modelo, cor, ano_veiculo):
        self.placa.set(placa)
        self.cor.set(cor)
        self.modelo.set(modelo)
        self.marca.set(marca)
        self.ano_veiculo.set(ano_veiculo)


class Adesivo:
    def __init__(self):
        self.id = ctk.StringVar()
        self.pessoal = Pessoal()
        self.veiculo = Veiculo()
        self.status = ctk.StringVar()
        self.ano = ctk.StringVar()

    def set(self, adesivo: str, status: str, ano: int, pessoal: Pessoal, veiculo: Veiculo):
        self.id.set(adesivo)
        self.pessoal.set(posto=pessoal.posto.get(), contato=pessoal.contato.get(),
                         nome_guerra=pessoal.nome_guerra.get(), nome_completo=pessoal.nome_completo.get(),
                         habilitacao=pessoal.habilitacao.get(), val_habilitacao=pessoal.val_habilitacao.get(),
                         setor=pessoal.setor.get(), om=pessoal.om.get(), saram=pessoal.saram.get())
        self.veiculo.set(ano_veiculo=veiculo.ano_veiculo.get(), placa=veiculo.placa.get(), marca=veiculo.marca.get(),
                         modelo=veiculo.modelo.get(), cor=veiculo.cor.get())
        self.status.set(status)
        self.ano.set(ano)


app = App()
app.mainloop()
