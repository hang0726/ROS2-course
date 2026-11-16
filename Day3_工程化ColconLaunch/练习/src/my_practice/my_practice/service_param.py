import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


# ===== 在这里写 AddServer / AddClient / ParamNode 三个类 =====
class AddServer(Node):
    def __init__(self):
        super().__init__('add_server')
        self.srv =  self.create_service(AddTwoInts, '/add_two_ints',self.add_callback)

    def add_callback(self,request,response):
        response.sum = request.a+request.b
        self.get_logger().info(f"a+b={request.a + request.b}")   # f-string 里要放表达式
        return response

class AddClient(Node):
    def __init__(self):
        super().__init__('add_client')
        self.cli = self.create_client(AddTwoInts,'/add_two_ints')   # 必须和服务端完全一致（小写 s）
        while not self.cli.wait_for_service(timeout_sec = 1.0):
            self.get_logger().info('等待服务器上线')
        self.req = AddTwoInts.Request()
        self.req.a = 2
        self.req.b=  3
    def run(self):
        future = self.cli.call_async(self.req)#call_async异步发送请求
        rclpy.spin_until_future_complete(self, future)
        #spin转起来until知道future结果complete完成
        self.get_logger().info(f'结果: 2+3={future.result().sum}')

class ParamNode(Node):
    def __init__(self):
        super().__init__('paramNode')
        self.declare_parameter('speed',0.5)
        self.timer_ = self.create_timer(1.0,self.report)
    def report(self):
        speed = self.get_parameter('speed').value
        #get_parameter，parameter是参数的意思 返回的是一个参数对象，`.value` 才是里面真正的数字。
        self.get_logger().info(f'当前speed = {speed}')     # info 不是 ingo



def main_server(args=None):
    rclpy.init(args=args)
    rclpy.spin(AddServer())
    rclpy.shutdown()


def main_client(args=None):
    rclpy.init(args=args)
    node = AddClient(); node.run(); node.destroy_node()
    rclpy.shutdown()


def main_param(args=None):
    rclpy.init(args=args)
    rclpy.spin(ParamNode())
    rclpy.shutdown()


if __name__ == '__main__':
    main_server()
