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

        self.img_back = ctk.CTkImage(Image.open("assets/icons/arrow_back_FILL0_wght400_GRAD0_opsz24.png"),
                                     size=(30, 30))

        self.user = User()
        self.input_adesivo = ctk.StringVar()
        self.exist_adesivo = False

        self.btn_back_to_search = ctk.CTkButton(self, text="Voltar", image=self.img_back, command=self.back_to_search)
        self.header_frame = HeaderFrame(master=self, fg_color='#1A55B1').pack(fill=ctk.X, expand=False, side=ctk.TOP)
        self.search_frame = SearchFrame(master=self, fg_color='transparent')
        self.search_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.information_frame = InformationFrame(master=self, width=350, height=150)

        ctk.CTkLabel(self, text='Developed by S2 Luiz Gabriel - V0.1').pack(fill=ctk.X, expand=False, side=ctk.BOTTOM)

    def search_adesivo(self):
        if len(self.input_adesivo.get()) > 4:
            path_sheet = DataHandler.load("url_sheet")
            if path_sheet:
                df = pd.read_excel(path_sheet)
                df.set_index("ADESIVO", inplace=True)

                if self.input_adesivo.get() in df.index:
                    self.exist_adesivo = True
                    ano_adesivo = df.loc[self.input_adesivo.get(), "ANO"]
                    nome_guerra = df.loc[self.input_adesivo.get(), "NOME DE GUERRA"]
                    nome_completo = df.loc[self.input_adesivo.get(), "NOME COMPLETO"]
                    posto = df.loc[self.input_adesivo.get(), "POSTO/GRAD"]
                    setor = df.loc[self.input_adesivo.get(), "SETOR"]
                    om = df.loc[self.input_adesivo.get(), "OM"]
                    contato = df.loc[self.input_adesivo.get(), "RAMAL"]
                    saram = int(df.loc[self.input_adesivo.get(), "SARAM"]) if not numpy.isnan(
                        df.loc[self.input_adesivo.get(), "SARAM"]) else ""
                    placa = df.loc[self.input_adesivo.get(), "PLACA"]
                    marca = df.loc[self.input_adesivo.get(), "MARCA"]
                    modelo = df.loc[self.input_adesivo.get(), "MODELO"]
                    habilitacao = df.loc[self.input_adesivo.get(), "HABILITAÇÃO"]
                    val_habilitacao = df.loc[self.input_adesivo.get(), "VALIDADE HAB."]
                    status = df.loc[self.input_adesivo.get(), "STATUS"]
                    cor = df.loc[self.input_adesivo.get(), "COR"]
                    ano_veiculo = df.loc[self.input_adesivo.get(), "ANO VEÍCULO"]

                    self.user.set(adesivo=self.input_adesivo.get(), ano_adesivo=ano_adesivo, nome_guerra=nome_guerra,
                                  nome_completo=nome_completo, posto=posto, setor=setor, om=om, contato=contato,
                                  saram=saram, placa=placa, modelo=modelo, marca=marca, ano_veiculo=ano_veiculo,
                                  cor=cor, habilitacao=habilitacao, val_habilitacao=val_habilitacao, status=status)
                    self.input_adesivo.set("")
                    self.btn_back_to_search.place(y=150, x=120, anchor=ctk.NW)
                    self.information_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
                    self.search_frame.place_forget()
                else:
                    self.exist_adesivo = False

    def search_adesivo_threaded(self):
        thread = threading.Thread(target=self.search_adesivo())
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
        ctk.CTkLabel(self, text='Célula de Contrainteligência e Segurança Orgânica', font=font_label_CCSO).grid(row=0,
                                                                                                                column=0,
                                                                                                                padx=10,
                                                                                                                sticky='w')
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

        status_label = ctk.CTkLabel(self, textvariable=master.exist_adesivo)
        btn_register = ctk.CTkButton(self, text='Cadastrar')
        """
        if master.exist_adesivo:
            status_label.grid(row=3, column=0, padx=10)
            btn_register.grid(row=3, column=1, padx=(0, 10))
        else:
        """



class InformationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ctk.CTkLabel(self, text="Informações pessoais", fg_color="gray30", width=550,
                     corner_radius=5).grid(row=0,
                                           column=0,
                                           padx=10,
                                           pady=(10, 0),
                                           sticky="nsew",
                                           columnspan=4)
        ctk.CTkLabel(self, text="Posto").grid(row=1, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Nome de Guerra").grid(row=1, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Nome Completo").grid(row=1, column=2, pady=1, padx=10, columnspan=2)
        ctk.CTkLabel(self, text="Organização Militar").grid(row=3, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Setor").grid(row=3, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Saram").grid(row=3, column=2, pady=1, padx=10)
        ctk.CTkLabel(self, text="Contato").grid(row=3, column=3, pady=1, padx=10)

        ctk.CTkLabel(self, textvariable=master.user.posto).grid(row=2, column=0, padx=10)
        ctk.CTkLabel(self, textvariable=master.user.nome_guerra).grid(row=2, column=1, padx=10)
        ctk.CTkLabel(self, textvariable=master.user.nome_completo).grid(row=2, column=2, padx=10, columnspan=2)

        ctk.CTkLabel(self, textvariable=master.user.om).grid(row=4, column=0, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.setor).grid(row=4, column=1, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.saram).grid(row=4, column=2, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.contato).grid(row=4, column=3, pady=(0, 3), padx=10)

        ctk.CTkLabel(self, text="Informações do Veiculo", fg_color="gray30", width=550,
                     corner_radius=5).grid(row=5,
                                           column=0,
                                           padx=10,
                                           pady=(
                                               10, 0),
                                           sticky="nsew",
                                           columnspan=4)
        ctk.CTkLabel(self, text="Placa").grid(row=6, column=0, pady=1, padx=10)
        ctk.CTkLabel(self, text="Marca").grid(row=6, column=1, pady=1, padx=10)
        ctk.CTkLabel(self, text="Modelo").grid(row=6, column=2, pady=1, padx=10)
        ctk.CTkLabel(self, text="Cor").grid(row=6, column=3, pady=1, padx=10)
        ctk.CTkLabel(self, text="Ano").grid(row=6, column=4, pady=1, padx=10)

        ctk.CTkLabel(self, textvariable=master.user.veiculo.placa).grid(row=7, column=0, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.veiculo.marca).grid(row=7, column=1, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.veiculo.modelo).grid(row=7, column=2, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.veiculo.cor).grid(row=7, column=3, pady=(0, 3), padx=10)
        ctk.CTkLabel(self, textvariable=master.user.veiculo.ano_veiculo).grid(row=7, column=4, pady=(0, 3), padx=10)

class User:
    def __init__(self):
        self.adesivo = ctk.StringVar()
        self.posto = ctk.StringVar()
        self.nome_guerra = ctk.StringVar()
        self.nome_completo = ctk.StringVar()
        self.setor = ctk.StringVar()
        self.om = ctk.StringVar()
        self.contato = ctk.StringVar()
        self.saram = ctk.StringVar()
        self.habilitacao = ctk.StringVar()
        self.val_habilitacao = ctk.StringVar()
        self.status = ctk.StringVar()

        self.veiculo = self.Veiculo()

    def set(self, adesivo, posto, nome_guerra, nome_completo, saram, contato, setor, om, habilitacao, val_habilitacao,
            placa, marca, modelo, cor, ano_adesivo, ano_veiculo, status):
        self.status.set(status)
        self.adesivo.set(adesivo)
        self.posto.set(posto)
        self.nome_guerra.set(nome_guerra)
        self.nome_completo.set(nome_completo)
        self.setor.set(setor)
        self.om.set(om)
        self.contato.set(contato)
        self.saram.set(saram)
        self.habilitacao.set(habilitacao)
        self.val_habilitacao.set(val_habilitacao)
        self.veiculo.set(placa=placa, marca=marca, modelo=modelo, cor=cor, ano_adesivo=ano_adesivo, ano_veiculo=ano_veiculo)


    class Veiculo:
        def __init__(self):
            self.placa = ctk.StringVar()
            self.cor = ctk.StringVar()
            self.marca = ctk.StringVar()
            self.modelo = ctk.StringVar()
            self.ano_adesivo = ctk.StringVar()
            self.ano_veiculo = ctk.StringVar()

        def set(self, placa, marca, modelo, cor, ano_adesivo, ano_veiculo):
            self.placa.set(placa)
            self.marca.set(marca)
            self.modelo.set(modelo)
            self.cor.set(cor)
            self.ano_veiculo.set(ano_veiculo)
            self.ano_adesivo.set(ano_adesivo)


# Widgets

# Search Frame Widgets

# Info Frame Widgets


app = App()
app.mainloop()
