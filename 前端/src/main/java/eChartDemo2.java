import com.alibaba.fastjson.JSON;

import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.nio.charset.StandardCharsets;

@WebServlet("/ec2")
public class eChartDemo2 extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        this.doGet(req,resp);
    }
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.setContentType("image/png");
        BufferedReader reader = req.getReader();
        String s1 = reader.readLine();
        Uid uid = JSON.parseObject(s1, Uid.class);
//        PrintWriter writer = resp.getWriter();
        ServletOutputStream outputStream = resp.getOutputStream();
        String image = "ok";
        if(uid!=null&&uid.getUsername()!=null) {
            image = new send().getImage(uid.getUsername());
        }else {
            System.out.println("空值");
            System.out.println(s1);
        }

    }
}
