global response

def ussd_red(text) :
        if text == '3' :
            response  = "CON "
            response += "1. Red Irish Potatoes \n"
            response += "2. White Irish Potatoes \n"                                              
            response += "3. Cowpeas \n"               
            response += "4. Carrots \n"

# price mechanism for Red Irish
        elif text == "3*1" :
            response  = "CON Source of seeds : \n"
            response += "1. Government \n"
            response += "2. Agrovet \n"  

        elif text == "3*1*1" or text == "3*1*2":
            response  = "CON Tractor : \n"
            response += "1. Own \n"
            response += "2. Hired \n"


        elif text == "3*1*1*1" or text == "3*1*1*2" or text == "3*1*2*1" or text == "3*1*2*1" or text == "3*1*2*2":
            response  = "CON Source of fertilizer : \n"
            response += "1. Government \n"
            response += "2. Agrovet \n"   
        
        elif text == "3*1*1*1*1" or text == "3*1*1*1*2" or text == "3*1*1*2*1" or text == "3*1*1*2*1" or text == "3*1*2*1*1" or text == "3*1*2*1*2"  or text == "3*1*2*2*1" or text == "3*1*2*2*2":
            response  = "CON Pesticide : \n"
            response += "1.Yes \n"
            response += "2. No \n"

        # start of block one of one 
        elif text == "3*1*1*1*1*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*1*1*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*1*2*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*1*2*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"
            # end of block one of one


        # start of block two of one
        elif text == "3*1*1*2*1*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*2*1*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*2*2*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*1*2*2*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"
        # end of block two of one


        # start of block one of two
        elif text == "3*1*2*1*1*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*1*1*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*1*2*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*1*2*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"
        # end of block one of two


        # start of block two of two
        elif text == "3*1*2*2*1*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*2*1*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*2*2*1" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"

        elif text == "3*1*2*2*2*2" :
                response  = "END Your production cost for Red Irish Potatoes per acre is Sh.X \n\n Thank you for using Farmula services"
        # end of block two of two
        return response