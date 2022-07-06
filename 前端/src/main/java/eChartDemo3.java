import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.nio.charset.StandardCharsets;

@WebServlet("/ec3")
public class eChartDemo3 extends HttpServlet {
    String s;
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
       this.doGet(req,resp);
    }
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
//        PrintWriter writer = resp.getWriter();
//        String s = ReaderMethod.readerMethod(new File("C:\\Users\\HP\\Desktop\\data\\angrysingle5668436889.json"));
//        writer.write(s);
        resp.setContentType("image/png");
        ServletOutputStream outputStream = resp.getOutputStream();
        FileInputStream fileInputStream = new FileInputStream("C:\\Users\\HP\\IdeaProjects\\untitled2\\src\\main\\resources\\user.png");
        byte[] bytes = new byte[1024];
        int len = 0;
        while ((len = fileInputStream.read(bytes)) != -1) {
            outputStream.write(bytes, 0, len);
        }
        fileInputStream.close();

    }
}
