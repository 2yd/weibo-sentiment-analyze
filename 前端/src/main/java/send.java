import java.io.*;
import java.net.Socket;

public class send {
    public static void main(String[] args) {
        send send = new send();
        String image = send.getImage("7089246227");

        System.out.println(image);

    }
    public String remoteCall(String pre,String content){
        // 访问服务进程的套接字
        Socket socket = null;
        String HOST="10.16.80.192";
        int PORT=10086;
        System.out.println("调用远程接口:host=>"+HOST+",port=>"+PORT);
        try {
            // 初始化套接字，设置访问服务的主机和进程端口号，HOST是访问python进程的主机名称，可以是IP地址或者域名，PORT是python进程绑定的端口号
            socket = new Socket(HOST, PORT);
            // 获取输出流对象
            OutputStream os = socket.getOutputStream();
            PrintStream out = new PrintStream(os);
            // 发送内容
            out.print(pre);
            out.print(content);
            // 告诉服务进程，内容发送完毕，可以开始处理
            out.print("over");
            // 获取服务进程的输入流
            InputStream is = socket.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(is,"utf-8"));
            String tmp = null;
            StringBuilder sb = new StringBuilder();
            // 读取内容
            while((tmp=br.readLine())!=null)
                sb.append(tmp).append('\n');
            // 解析结果
            String res = sb.toString();
            return res;
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {if(socket!=null) socket.close();} catch (IOException e) {}
            System.out.println("远程接口调用结束.");
        }
        return null;
    }
    public String remoteCloudCall(String pre,String content,String CloudName){
        // 访问服务进程的套接字
        Socket socket = null;
        String HOST="10.16.80.192";
        int PORT=10086;
        System.out.println("调用远程接口:host=>"+HOST+",port=>"+PORT);
        try {
            // 初始化套接字，设置访问服务的主机和进程端口号，HOST是访问python进程的主机名称，可以是IP地址或者域名，PORT是python进程绑定的端口号
            socket = new Socket(HOST, PORT);
            // 获取输出流对象
            OutputStream os = socket.getOutputStream();
            PrintStream out = new PrintStream(os);
            // 发送内容
            String ss=content+CloudName;
            out.print(pre);
            out.print(ss);
            // 告诉服务进程，内容发送完毕，可以开始处理
            out.print("over");
            // 获取服务进程的输入流
            InputStream is = socket.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(is,"utf-8"));
            String tmp = null;
            StringBuilder sb = new StringBuilder();
            // 读取内容
            while((tmp=br.readLine())!=null)
                sb.append(tmp).append('\n');
            // 解析结果
            String res = sb.toString();
            return res;
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {if(socket!=null) socket.close();} catch (IOException e) {}
            System.out.println("远程接口调用结束.");
        }
        return null;
    }


    public String getImage(String content){
        // 访问服务进程的套接字
        Socket socket = null;
        String HOST="10.16.80.192";
        int PORT=10086;
        System.out.println("调用远程接口:host=>"+HOST+",port=>"+PORT);
        try {
            // 初始化套接字，设置访问服务的主机和进程端口号，HOST是访问python进程的主机名称，可以是IP地址或者域名，PORT是python进程绑定的端口号
            socket = new Socket(HOST, PORT);
            // 获取输出流对象
            OutputStream os = socket.getOutputStream();
            PrintStream out = new PrintStream(os);
            // 发送内容
            out.print("wor");
            out.print(content);
            // 告诉服务进程，内容发送完毕，可以开始处理
            out.print("over");
            // 获取服务进程的输入流
            InputStream is = socket.getInputStream();
            //BufferedReader br = new BufferedReader(new InputStreamReader(is,"utf-8"));
            File file = new File("C:\\Users\\HP\\IdeaProjects\\untitled2\\src\\main\\resources\\user.png");
            FileOutputStream fos = new FileOutputStream(file);
            try{
                byte[] buf = new byte[1024];
                //记录实际读取到的字节
                int n = 0;
                //循环读取
                while((n = is.read(buf)) != -1){
                    //输出到指定文件
                    fos.write(buf,0,n);
               //     System.out.println("读取一次数据");
                }
             //   System.out.println("图片读取成功");
                fos.close();
            }catch (Exception e){
                e.printStackTrace();
            }
//            String tmp = null;
//            StringBuilder sb = new StringBuilder();
//            // 读取内容
//            while((tmp=br.readLine())!=null)
//                sb.append(tmp).append('\n');
//            // 解析结果
//            String res = sb.toString();
            String res="ok";
            return res;
        } catch (IOException e) {
            e.printStackTrace();
            return "no";
        } finally {
            try {if(socket!=null) socket.close();
            } catch (IOException e) {}
            System.out.println("远程接口调用结束.");

        }

    }


}
