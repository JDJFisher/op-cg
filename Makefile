
all:
	exit

fseq: # temp for development 
	python3 opcg seq -vdm -soa examples/fortran/airfoil/airfoil.F90 -Iexamples/fortran/airfoil/ -o temp/

fcuda: # temp for development 
	python3 opcg cuda -vdm examples/fortran/airfoil/airfoil.F90 -Iexamples/fortran/airfoil/ -o temp/

cseq: # temp for development 
	python3 opcg seq -vd examples/cpp/airfoil/airfoil.cpp -Iexamples/cpp/airfoil/ -o temp/

install:
	pip3 install -r requirements.txt

alias:
	echo 'Create an alias with this' 
	alias opcg="python3 ${CURDIR}/opcg"

lint:
	mypy opcg
	pylint opcg --indent-string='  '

test:
	pytest

clean:
	rm -r temp/*