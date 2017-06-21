/* Add your Application JavaScript */
$(document).ready(function(){
    $('#newTitle').click(function(){
        newProject();
    });
});

function newProject(){
    var series= $('#series').val();
    console.log("Series: "+series);
    var fulltitle= $('#fulltitle').val();
    console.log("FTitle: "+fulltitle);
    var subtitle= $('#subtitle').val();
    console.log("subtitle: "+subtitle);
    var shorttitle= $('#shorttitle').val();
    console.log("shorttitle: "+shorttitle);
    var company= $('#company').val();
    console.log("company: "+company);   
    var publisher=$('#publisher').val();
    console.log("publisher: "+publisher);
    var editions= $('#editions').val();
    console.log("editions: "+editions);
    var vol=$("#vol").val();
    console.log("vol: "+vol);
    var clas=$("#class").val();
    console.log("class: "+clas);
    var format=$("#format").val();
    console.log("format: "+format);
    var pud_date= $("#pud_date").val();
    console.log("pud_date: "+pud_date);
    var work =$("#work").val();
    console.log("work: "+work);
    var EAN_ISBN= $("#EAN_ISBN-13").val();
    console.log("EAN_ISBN-13: "+EAN_ISBN);
    var season= $("#season").val();
    console.log("season: "+season);
    var ISBN= $("#ISBN-10").val();
    console.log("ISBN-10: "+ISBN);
    var bisac_status= $("#bisac_status").val();
    console.log("bisac_status: "+bisac_status);
    var page_count=$("#page_count").val();
    console.log("page_count: "+page_count);
    var trim= $("#trim").val();
    console.log("trim: "+trim);
    var note=$("#note").val();
    console.log("note: "+note);
    var cover= $("#file").files;
    console.log("file: "+cover);
}