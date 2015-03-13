# Introduction #

Add your content here.


# Details #

Add your content here.  Format your content with:
  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages

```
-module(tcp_proxy).

-include_lib("orber/src/orber_iiop.hrl").

-export([start/0,loop/3,listen/3,one_socket/1]).


start() ->
    spawn(?MODULE, listen,[]).

listen(Sport,TargetIP,Tport) ->
    {ok, LSock} = gen_tcp:listen(Sport, [{reuseaddr,true},binary, {packet, 0}, 
                                        {active, false}]),
    loop(LSock,TargetIP,Tport).
    
loop(LSock,TargetIP,Tport) ->
    {ok, Sock} = gen_tcp:accept(LSock),
    io:format("tcp_proxy: source connect ~p~n",[Sock]),

    {ok, SockTarget} = gen_tcp:connect(TargetIP,Tport, [binary, {packet, 0}]),      
    Pid = spawn(?MODULE,one_socket,[{Sock,SockTarget}]),
    inet:setopts(Sock, [{active, true}]),
    inet:setopts(SockTarget, [{active, true}]),
    gen_tcp:controlling_process(SockTarget, Pid),
    gen_tcp:controlling_process(Sock, Pid),
    io:format("tcp_proxy: target ~p handler ~p~n",[SockTarget,Pid]), 
    loop(LSock,TargetIP,Tport).

debug_http(ID,Bytes)->
    String = binary_to_list(Bytes),
    {ok,[Headers|_]} = regexp:split(String,"\r\n\r\n"),
    io:format("~s~s~n",[ID,Headers]).

debug_bytes(ID,Bytes= <<"GIOP",_/binary>>)->
    % need to trap location_forward exception from request, dec_target_key
    M = cdr_decode:dec_message(any:create(),Bytes),
    io:format("~s~p~n",[ID,M]);
debug_bytes(ID,Bytes= <<"GET",_/binary>>)->debug_http(ID,Bytes);
debug_bytes(ID,Bytes= <<"POST",_/binary>>)->debug_http(ID,Bytes);
debug_bytes(ID,Bytes= <<"HTTP",_/binary>>)->debug_http(ID,Bytes);
debug_bytes(ID,Bytes) ->
    String = binary_to_list(Bytes),
    io:format("~s~s~n",[ID,string:substr(String,1,100)]).

	
one_socket({SockSource,SockTarget})->
    receive
        {tcp, SockSource, Bytes} ->
            debug_bytes("s ",Bytes),
            gen_tcp:send(SockTarget, Bytes),
            one_socket({SockSource,SockTarget});
        {tcp, SockTarget, Bytes} ->
            debug_bytes("t ",Bytes),
            gen_tcp:send(SockSource, Bytes),
            one_socket({SockSource,SockTarget});
        Other ->
            io:format("tcpproxy: got msg ~p~n", [Other])
    end.

```