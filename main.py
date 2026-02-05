from office_sud_kz.main import run as officeSudRunner
import multiprocessing

def main():
    officeSudRunner()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    multiprocessing.freeze_support()
    main()

    input("Готово!")
