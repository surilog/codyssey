from mini_redis import MiniRedis


class RedisCommandExecutor:
    def __init__(self, redis_engine: MiniRedis):
        self.redis = redis_engine
    def execute(self, cmd_tokens: list) -> str:
        if not cmd_tokens:
            return ""
        # 사용자가 CLI입력한 줄을 공백 기준으로 잘라 만든 리스트 == cmd_tokens
        cmd_name = cmd_tokens[0].upper()
        args = cmd_tokens[1:] 

        # do_SET , do_GET 형태의 메서드를 클래스 내에서 자동으로 찾음
        handler =getattr(self, f"do_{cmd_name}",None)
        if not handler:
            return f"(error) ERR unknown command '{cmd_tokens[0]}'"
        return handler(args)
    
    
    def _err_args(self, cmd_name: str) -> str:
        return f"(error) ERR wrong number of arguments for '{cmd_name}' command"
    def _err_int_args(self) -> str:
        return "(error) ERR value is not an integer or out of range"
    def _err_int_range(self) -> str:
        return "(error) ERR value is not an integer or out of range"
    def _check_args(self, args:list, expected: int, cmd_name: str) -> str | None:
            if len(args) != expected:
                return self._err_args(cmd_name)
            return None
    def do_SET(self, args:list) -> str:
        if len(args) < 2:
            return self._err_args("set")

        key = args[0]
        value = args[1]
        ttl = None

        if len(args) >=4 and args[2].upper() == "EX":
            try:
                ttl = int(args[3])
            except ValueError:
                return self._err_int_range()
                
        return self.redis.set(key, value,ttl=ttl )

    def do_GET(self, args:list) -> str:
        if len(args) != 1:
            return self._err_args("get")

        val = self.redis.get(args[0])
        return "(nil)" if val is None else f'"{val}"'

    def do_DEL(self, args:list) -> str:

        if len(args) != 1:
            return self._err_args("del")

        count = self.redis.delete(args[0])
        return f"(integer) {count}"

    def do_EXISTS(self, args: list) -> str:
       
        if len(args) != 1:
            return self._err_args("exists")

        res = self.redis.exists(args[0])
        return f"(integer) {res}"

    def do_DBSIZE(self, args: list) ->str:
        if len(args) != 0:
            return self._err_args("dbsize")

        size = self.redis.dbsize()
        return f"(integer) {size}"

    def do_KEYS(self, args:list) ->str:
        if len(args) != 0:
            return self._err_args("keys")

        key_list = self.redis.keys()
        if not key_list:
            return "(empty array)"

        lines = [f'{i+1}) "{k}"' for i, k in enumerate(key_list)]
        return "\n".join(lines)

    def do_CONFIG(self, args:list) -> str:
        if len(args) == 3 and args[0].upper() == "SET":
            param_name = args[1].lower()
            if param_name == "maxmemory":
                try:
                    bytes_val = int(args[2])
                    return self.redis.config_set_maxmemory(bytes_val)
                except ValueError:
                    return self._err_int_range()
        return "(error) ERR wrong number of arguments or section for 'config'"

    def do_INFO(self, args:list) -> str:
        if len(args) == 1 and args[0].lower() =="memory":
            info = self.redis.info_memory()
            return(
                f"used_memory : {info['used_memory']}\n "
                f"maxmemory:{info['maxmemory']}\n"
                f"evicted_keys:{info['evicted_keys']}"
            )
        return "(error) ERR wrong number of arguments or selection for 'info'"

    def do_EXPIRE(self, args:list) -> str:
            if len(args) !=2:
                return self._err_args("expire")

            try:
                seconds = int(args[1])
            except ValueError:
                return self._err_int_range()
            res = self.redis.expire(args[0], seconds)
            return f"(integer) {int(res)}"

    def do_TTL(self, args:list) -> str:
        if len(args) != 1:
            return self._err_args("ttl")

        res = self.redis.ttl(args[0])
        return f"(integer) {res}"
    
    def do_LPUSH(self, args:list) -> str:
        if err:= self._check_args(args,2,"lpush"):
            return err
        try:
            size = self.redis.lpush(args[0],args[1])
            return f"(integer) {size}"
        except TypeError as e:
            return f"(error) {str(e)}"

    def do_LPOP(self, args:list)->str:
        if err:= self._check_args(args, 1, "lpop"):
            return err
        val = self.redis.lpop(args[0])
        return "(nil)" if val is None else f'"{val}"'

    def do_LRANGE(self, args: list) -> str:
        if len(args) != 3:
            return self._check_args(args, 3, "lrange")
        try:
            start, stop = int(args[1]), int(args[2])
        except ValueError:
            return "(error) ERR value is not an integer or out of range"

        items = self.redis.lrange(args[0], start, stop)
        if not items:
            return "(empty array)"
        return "\n".join([f'{i+1}) "{item}"' for i, item in enumerate(items)])

    def do_SUBSCRIBE(self, args: list) ->str:
        if len(args) <1 :
            return self._check_args(args, 1,"subscribe")

        client_id = "cli_client"
        responses = []
        for ch in args:
            count = self.redis.subscribe(client_id,ch)
            responses.append(f'1) "subscribe"\n2) "{ch}"\n3) (integer) {count}')
        return "\n".join(responses)

    def do_UNSUBSCRIBE(self, args:list)->str:
        if len(args) <1 :
            return self._check_args(args, 1, "unsubscribe")
        client_id = "cli_client"
        responses = []
        for ch in args:
            count = self.redis.unsubscribe(client_id,ch)
            responses.append(f'1) "unsubscribe"\n2) "{ch}"\n3) (integer) {count}')

        return "\n".join(responses)

    def do_PUBLISH(self, args: list) -> str:
        if len(args) !=2:
            return self._check_args(args,2,"publish")

        channel = args[0]
        message = args[1]
        receivers = self.redis.publish(channel, message) #메시지 전달받은 총 구독자 수

        output = [f"(integer) {receivers}"]
        client_id = "cli_client"
        chan_list = self.redis.pubsub.client_channels.get(client_id)
        if chan_list:
            curr = chan_list.dummy_head.next
            while curr != chan_list.dummy_tail:
                if curr.key == channel:
                    output.insert(0,f'[메시지수신]\n1) "message"\n2 "{channel}"\n3 " {message}"')
                    break
                curr = curr.next
        return "\n".join(output)

    def do_PUBSUB(self, args: list) -> str:
        if len(args) ==1 and args[0].upper() == "CHANNELS":
            ch_list = self.redis.pubsub_channels()
            if not ch_list:
                return ("empty array")
            return "\n".join([f'{i+1}) "{ch}"'for i, ch in enumerate(ch_list)])

        return "(error) ERR unknown subcommand or wrong argumentsfor 'pubsub'"

    def do_ZADD(self, args:list) -> str:
        if len(args) !=3:
            return "(error) ERR wrong number of arguments for 'zadd' command"
        key, score_str, member = args[0], args[1], args[2]
        try:
            score = float(score_str)
        except ValueError:
            return "(error) ERR value is not a valid float or integer"
        self.redis.zadd(key, score, member)
        return "(integer) 1"

    def do_ZRANGE(self, args: list) -> str:
        if len(args) != 1:
            return "(error) ERR wrong number of arguments for 'zrange' command"
        key = args[0]
        members = self.redis.zrange(key)
        if not members:
            return "(empty list or set)"

        lines = [f'{i+1}) "{m}" (Score : {s})' for i , (s,m) in enumerate(members)]
        return "\n".join(lines)