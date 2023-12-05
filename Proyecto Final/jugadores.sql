create database jugadores;
use jugadores;

create table jugador(
	nombre varchar(50) NOT NULL PRIMARY KEY,
    edad int, 
    posicion varchar(60),
    nacionalidad varchar(40));
    
create table equipos(
	nombre varchar(50) NOT NULL,
    equipo varchar (60),
    foreign key (nombre) references jugador(nombre));
    
create table valores(
	nombre varchar(50) NOT NULL,
    valor_mercado_millones int(40) NOT NULL,
    foreign key (nombre) references jugador (nombre));

select * from jugador;
select * from equipos;
select * from valores;

drop database jugadores;