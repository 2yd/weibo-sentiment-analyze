import com.alibaba.fastjson.JSON;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet("/ec4")
public class eChartDemo4 extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        this.doGet(req,resp);
    }
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {

       req.setCharacterEncoding("gbk");
        BufferedReader reader = req.getReader();
        String s1 = reader.readLine();
//        Uid uid = JSON.parseObject(s1, Uid.class);
        User user = JSON.parseObject(s1, User.class);
        PrintWriter writer = resp.getWriter();
        String s =new send().remoteCloudCall("edi",user.getUsername(),user.getCloudname());
        System.out.println(user);
        writer.write(s);
    }
}

