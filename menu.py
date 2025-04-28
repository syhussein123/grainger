#!/usr/bin/env python3
"""
Grainger Menu Widget Prototype
A collapsible menu/sidebar widget prototype for customer service representatives
to quickly look up products, alternatives, and frequently bought together items.
"""


import sys
import os
import time
import json
from typing import Dict, List, Any


# ANSI color codes for terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'




# Mock product database
PRODUCT_DB = {
    "HWN5400": {
        "name": "Honeywell North Hook-and-Loop (4-Point), Threaded, M/L Mask Size, 5400",
        "category": "respirators",
        "price": "$223.26/each",
        "stock": 345,
        "rating": 4.8,
        "sku": "HWN5400",
        "description": "NIOSH-approved N95 particulate respirator with Cool Flow™ valve for easier breathing. Ideal for sanding, grinding, and dusty work environments.",
        "frequently_bought_together": ["3MFIT", "3MWIPE", "SAFEGLS01"],
        "alternatives": ["3M8210", "4DA45", "MOLDX2700N95"]
    },
    "PASPECML": {
        "name": "Bullard Silicone, Threaded, M Mask Size, Silicone, Spectrum",
        "category": "respirators",
        "price": "$536.17/each",
        "stock": 345,
        "rating": 4.6,
        "sku": "PASPECML",
        "description": "NIOSH-approved N95 particulate respirator with Cool Flow™ valve for easier breathing. Ideal for sanding, grinding, and dusty work environments.",
        "frequently_bought_together": ["3MFIT", "3MWIPE", "SAFEGLS01"],
        "alternatives": ["3M8210", "4DA45", "MOLDX2700N95"]
    },
    "SCT2000": {
        "name": "Scott EDPM Rubber, Bayonet, Polyester AV-2000",
        "category": "respirators",
        "price": "$223.26/each",
        "stock": 345,
        "rating": 4.5,
        "sku": "SCT2000",
        "description": "NIOSH-approved N95 particulate respirator with Cool Flow™ valve for easier breathing. Ideal for sanding, grinding, and dusty work environments.",
        "frequently_bought_together": ["3MFIT", "3MWIPE", "SAFEGLS01"],
        "alternatives": ["3M8210", "4DA45", "MOLDX2700N95"]
    },
    "MOLDX2700N95": {
        "name": "Moldex® Thermoplastic 9000 Respirator",
        "category": "respirators",
        "price": "$234.35/ each",
        "stock": 210,
        "rating": 4.6,
        "sku": "MOLDX2700N95",
        "description": "NIOSH-approved N95 particulate respirator with Dura-Mesh shell to maintain shape. Excellent for construction and manufacturing.",
        "frequently_bought_together": ["MOLDXWIPE", "SAFEGLS01", "GLOVE100"],
        "alternatives": ["HWN5400", "3M8210", "HWN95"]
    },
    "4DA45": {
        "name": "3M Silicone/Thermoplastic Elastomer, Bayonet, Thermoplastic Elastomer",
        "category": "respirators",
        "price": "$214.28/ each",
        "stock": 210,
        "rating": 4.6,
        "sku": "4DA45",
        "description": "NIOSH-approved N95 particulate respirator with Dura-Mesh shell to maintain shape. Excellent for construction and manufacturing.",
        "frequently_bought_together": ["MOLDXWIPE", "SAFEGLS01", "GLOVE100"],
        "alternatives": ["HWN5400", "3M8210", "HWN95"]
    },
    "3M8210": {
        "name": "3M Silicone/Thermoplastic Elastomer, Bayonet, M Mask Size, Advantage 6000",
        "category": "respirators",
        "price": "$254.28/each",
        "stock": 187,
        "rating": 4.7,
        "sku": "3M8210",
        "description": "NIOSH-approved N95 particulate respirator without valve. Economical choice for general dust protection.",
        "frequently_bought_together": ["3MWIPE", "SAFEGLS01", "GLOVE100"],
        "alternatives": ["HWN5400", "MOLDX2700N95", "HWN95"]
    },
    "3MFIT": {
        "name": "3M™ Fit Testing Kit",
        "category": "safety_equipment",
        "price": "$556.07//kit",
        "stock": 42,
        "rating": 4.9,
        "sku": "3MFIT",
        "description": "Complete kit for qualitative fit testing of respirators. Includes sweet and bitter solutions, hood, and nebulizers.",
        "frequently_bought_together": ["HWN5400", "3M6000", "RESPLOG"],
        "alternatives": ["ALLEGRO1000", "MSAMFT"]
    },
    "3MWIPE": {
        "name": "3M™ Respirator Cleaning Wipes",
        "category": "maintenance",
        "price": "$12.75/box of 40",
        "stock": 189,
        "rating": 4.5,
        "sku": "3MWIPE",
        "description": "Alcohol-free wipes for cleaning respirators and safety glasses. Safe for most respirator materials.",
        "frequently_bought_together": ["HWN5400", "SAFEGLS01", "GLOVE100"],
        "alternatives": ["MOLDXWIPE", "HONWIPE"]
    },
    "SAFEGLS01": {
        "name": "SecureFit™ Safety Glasses, Clear Lens",
        "category": "eye_protection",
        "price": "$9.99/pair",
        "stock": 523,
        "rating": 4.7,
        "sku": "SAFEGLS01",
        "description": "Lightweight safety glasses with self-adjusting temples for secure fit. Anti-fog coating and meets ANSI Z87.1 standards.",
        "frequently_bought_together": ["HWN5400", "EYECLN", "GLOVE100"],
        "alternatives": ["UVXS3900", "PYRSAFE", "MCRSAFE"]
    },
    "HWN95": {
        "name": "Honeywell N95 Disposable Respirator",
        "category": "respirators",
        "price": "$21.75/box of 10",
        "stock": 95,
        "rating": 4.5,
        "sku": "HWN95",
        "description": "NIOSH-approved N95 respirator with foam face seal for improved comfort and fit. Includes adjustable nose bridge.",
        "frequently_bought_together": ["HONWIPE", "SAFEGLS01", "GLOVE100"],
        "alternatives": ["HWN5400", "3M8210", "MOLDX2700N95"]
    },
    "GLOVE100": {
        "name": "PowerGrip™ Nitrile Gloves",
        "category": "hand_protection",
        "price": "$12.50/box of 100",
        "stock": 412,
        "rating": 4.8,
        "sku": "GLOVE100",
        "description": "Disposable nitrile gloves with textured fingertips for improved grip. Powder-free and 5 mil thickness.",
        "frequently_bought_together": ["HWN5400", "SAFEGLS01", "APRON01"],
        "alternatives": ["GLOVE200", "GLOVELAT", "NITRISTRONG"]
    },
    "HAMMER1": {
        "name": "DeWalt 20oz Steel Framing Hammer",
        "category": "hand_tools",
        "price": "$29.99/unit",
        "stock": 74,
        "rating": 4.9,
        "sku": "HAMMER1",
        "description": "Professional-grade steel framing hammer with vibration-absorbing grip and milled face.",
        "frequently_bought_together": ["NAILS3", "TSQUARE", "GLOVE200"],
        "alternatives": ["HAMMER2", "HAMMERPRO", "ESTWING1"]
    },
    "DRILL1": {
        "name": "Milwaukee 18V 1/2\" Cordless Drill Kit",
        "category": "power_tools",
        "price": "$159.99/kit",
        "stock": 36,
        "rating": 4.9,
        "sku": "DRILL1",
        "description": "Heavy-duty 18V cordless drill with 2 batteries, charger and carrying case. 550 in-lbs torque.",
        "frequently_bought_together": ["BITS1", "DRILLCASE", "BATTERY18V"],
        "alternatives": ["DRILL2", "DEWDRILL", "MAKDRILL"]
    },
    "DRILL2": {
        "name": "Milwaukee 18V 1/2\" Cordless Drill Kit",
        "category": "power_tools",
        "price": "$159.99/kit",
        "stock": 36,
        "rating": 4.9,
        "sku": "DRILL1",
        "description": "Heavy-duty 18V cordless drill with 2 batteries, charger and carrying case. 550 in-lbs torque.",
        "frequently_bought_together": ["BITS1", "DRILLCASE", "BATTERY18V"],
        "alternatives": ["DRILL2", "DEWDRILL", "MAKDRILL"]
    },
    "DEWDRILL": {
        "name": "Milwaukee 18V 1/2\" Cordless Drill Kit",
        "category": "power_tools",
        "price": "$159.99/kit",
        "stock": 36,
        "rating": 4.9,
        "sku": "DRILL1",
        "description": "Heavy-duty 18V cordless drill with 2 batteries, charger and carrying case. 550 in-lbs torque.",
        "frequently_bought_together": ["BITS1", "DRILLCASE", "BATTERY18V"],
        "alternatives": ["DRILL2", "DEWDRILL", "MAKDRILL"]
    },
    "MAKDRILL": {
        "name": "Milwaukee 18V 1/2\" Cordless Drill Kit",
        "category": "power_tools",
        "price": "$159.99/kit",
        "stock": 36,
        "rating": 4.9,
        "sku": "DRILL1",
        "description": "Heavy-duty 18V cordless drill with 2 batteries, charger and carrying case. 550 in-lbs torque.",
        "frequently_bought_together": ["BITS1", "DRILLCASE", "BATTERY18V"],
        "alternatives": ["DRILL2", "DEWDRILL", "MAKDRILL"]
    },
    "WRENCH1": {
        "name": "Craftsman 20pc SAE & Metric Combination Wrench Set",
        "category": "hand_tools",
        "price": "$89.99/set",
        "stock": 53,
        "rating": 4.7,
        "sku": "WRENCH1",
        "description": "Chrome-vanadium steel wrench set with SAE and metric sizes. Includes storage case and lifetime warranty.",
        "frequently_bought_together": ["SOCKET1", "TOOLBOX1", "WRENCHORG"],
        "alternatives": ["WRENCH2", "SNAPW", "GEARW"]
    }
}




# Sample search index for quick lookup
SEARCH_INDEX = {
    "full face respirator": ["HWN5400", "PASPECML", "SCT2000"],
    "gloves": ["GLOVE100", "GLOVE200", "GLOVELAT", "NITRISTRONG"],
    "n95": ["HWN5400", "MOLDX2700N95", "3M8210", "HWN95"],
    "safety glasses": ["SAFEGLS01", "UVXS3900", "PYRSAFE", "MCRSAFE"],
    "hammer": ["HAMMER1", "HAMMER2", "HAMMERPRO", "ESTWING1"],
    "drill": ["DRILL1", "DRILL2", "DEWDRILL", "MAKDRILL"],
    "wrench": ["WRENCH1", "WRENCH2", "SNAPW", "GEARW"],
    "tool": ["HAMMER1", "DRILL1", "WRENCH1", "TOOLBOX1"],
    "dewalt": ["HAMMER1", "DEWDRILL"],
    "milwaukee": ["DRILL1"],
    "3m": ["HWN5400", "3MFIT", "3MWIPE", "3M8210"],
    "fit test": ["3MFIT", "ALLEGRO1000", "MSAMFT"],
    "cleaning": ["3MWIPE", "MOLDXWIPE", "HONWIPE"],
    "moldex": ["MOLDX2700N95", "MOLDXWIPE"],
    "kit": ["3MFIT", "DRILL1"]
}

class GraingerWidget:
    """Grainger Menu Toolbar for Customer Service Representatives"""
   
    def __init__(self):
        self.products = PRODUCT_DB
        self.search_index = SEARCH_INDEX
        self.current_customer = None
        self.last_results = []
        self.widget_visible = True
   
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
   
    def display_header(self):
        """Display the widget header"""
        print(f"{Colors.HEADER}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗")
        print(f"║                GRAINGER REP TOOLBAR                        ║")
        print(f"╚════════════════════════════════════════════════════════════╝{Colors.ENDC}")
       
    def display_menu(self):
        """Display the main menu options"""
        print(f"\n{Colors.BOLD}QUICK COMMANDS:{Colors.ENDC}")
        print(f"{Colors.GREEN}[P]{Colors.ENDC} Product lookup")
        print(f"{Colors.GREEN}[Q]{Colors.ENDC} Quit widget")
        print(f"{Colors.GREEN}[/]{Colors.ENDC} Toggle widget visibility")
   
    def search_products(self, query: str) -> List[str]:
        """Search for products based on query"""
        query = query.lower()
        results = []
       
        # Direct SKU lookup
        if query in [p.lower() for p in self.products.keys()]:
            for sku in self.products:
                if sku.lower() == query:
                    return [sku]
       
        # Search index lookup
        for term, skus in self.search_index.items():
            if query in term or term in query:
                results.extend(skus)
       
        # Remove duplicates while preserving order
        unique_results = []
        for sku in results:
            if sku not in unique_results:
                unique_results.append(sku)
       
        return unique_results
   
    def display_product(self, sku: str, is_alternative=False):
        """Display detailed product information"""
        if sku not in self.products:
            print(f"{Colors.RED}Product SKU {sku} not found.{Colors.ENDC}")
            return
        
        product = self.products[sku]
        print(f"\n{Colors.BOLD}{Colors.BLUE}══════ PRODUCT DETAILS ══════{Colors.ENDC}")
        print(f"{Colors.BOLD}Product:{Colors.ENDC} {product['name']} ({sku})")
        print(f"{Colors.BOLD}Price:{Colors.ENDC} {product['price']} | {Colors.BOLD}Score:{Colors.ENDC} {product['rating']}/5.0")
        
        if product['stock'] > 100:
            stock_color = Colors.GREEN
        elif product['stock'] > 20:
            stock_color = Colors.YELLOW
        else:
            stock_color = Colors.RED
        
        print(f"{Colors.BOLD}Stock:{Colors.ENDC} {stock_color}{product['stock']} units{Colors.ENDC}")
        print(f"{Colors.BOLD}Description:{Colors.ENDC} {product['description']}")

        print(f"\n{Colors.BOLD}OTHER OPTIONS:{Colors.ENDC}")
        print(f"{Colors.GREEN}[F]{Colors.ENDC} Frequently Bought Together")
        # Only show Alternatives option if this isn't being viewed as an alternative itself
        if not is_alternative:
            print(f"{Colors.GREEN}[A]{Colors.ENDC} Alternatives")
        print(f"{Colors.GREEN}[B]{Colors.ENDC} Back to search results")
        print(f"{Colors.GREEN}[M]{Colors.ENDC} Main menu")
        
        # Return the product SKU for use in handle_product_options
        return sku

    def handle_product_options(self, sku: str, is_alternative=False):
        """Handle options after displaying a product"""
        while True:
            command = input(f"\n{Colors.GREEN}Command:{Colors.ENDC} ").lower()
            
            if command == 'f':
                self.display_frequently_bought_together(sku)
                input(f"\n{Colors.CYAN}Press Enter to return to product options...{Colors.ENDC}")
                # Re-display the product after showing frequently bought together items
                self.display_product(sku, is_alternative)
            elif command == 'a' and not is_alternative:
                self.display_alternatives(sku)
                input(f"\n{Colors.CYAN}Press Enter to return to product options...{Colors.ENDC}")
                # Re-display the product after showing alternatives
                self.display_product(sku, is_alternative)
            elif command == 'b':
                # Go back to search results
                return 'back'
            elif command == 'm':
                # Return to main menu
                return 'menu'
            else:
                print(f"{Colors.YELLOW}Invalid command. Please try again.{Colors.ENDC}")
    
    def display_frequently_bought_together(self, sku: str):
        """Display frequently bought together items"""
        if sku not in self.products:
            print(f"{Colors.RED}Product SKU {sku} not found.{Colors.ENDC}")
            return
       
        product = self.products[sku]
        fbt_skus = product.get('frequently_bought_together', [])
       
        print(f"\n{Colors.BOLD}{Colors.BLUE}══════ FREQUENTLY BOUGHT TOGETHER WITH {sku} ══════{Colors.ENDC}")
        print(f"{Colors.BOLD}Product:{Colors.ENDC} {product['name']}")
       
        if not fbt_skus:
            print(f"{Colors.YELLOW}No frequently bought together items found for this product.{Colors.ENDC}")
            return
       
        for i, fbt_sku in enumerate(fbt_skus, 1):
            if fbt_sku in self.products:
                fbt_product = self.products[fbt_sku]
                print(f"\n{i}. {Colors.BOLD}{fbt_product['name']}{Colors.ENDC} ({fbt_sku})")
                print(f"   Price: {fbt_product['price']} | Stock: {fbt_product['stock']} units")
               
               
            else:
                print(f"{i}. {Colors.YELLOW}SKU: {fbt_sku} (Product data not available){Colors.ENDC}")
       
        # Quick copy suggestion for email
        primary_name = product['name']
        if fbt_skus and fbt_skus[0] in self.products:
            suggestion = f"Based on your interest in {primary_name}, many customers also purchase {self.products[fbt_skus[0]]['name']} for optimal performance."
            print(f"\n{Colors.CYAN}Suggested text for customer email:{Colors.ENDC}")
            print(f"\"{suggestion}\"")
           
        # Add an option to view one of the frequently bought together products
        print(f"\n{Colors.BOLD}COMMANDS:{Colors.ENDC}")
        print(f"{Colors.GREEN}[number]{Colors.ENDC} View product details")
        print(f"{Colors.GREEN}[B]{Colors.ENDC} Back to original product")
       
        command = input(f"\n{Colors.GREEN}Command:{Colors.ENDC} ").lower()
       
        if command.isdigit() and 1 <= int(command) <= len(fbt_skus):
            selected_sku = fbt_skus[int(command) - 1]
            if selected_sku in self.products:
                # Display the selected product and handle its options
                selected_product_sku = self.display_product(selected_sku)
                self.handle_product_options(selected_product_sku)
        # For 'b' or any other command, function returns to caller
   
    def display_alternatives(self, sku: str):
        """Display alternative products"""
        if sku not in self.products:
            print(f"{Colors.RED}Product SKU {sku} not found.{Colors.ENDC}")
            return
       
        product = self.products[sku]
        alt_skus = product.get('alternatives', [])
       
        print(f"\n{Colors.BOLD}{Colors.BLUE}══════ ALTERNATIVES TO {sku} ══════{Colors.ENDC}")
        print(f"{Colors.BOLD}Product:{Colors.ENDC} {product['name']}")
        print(f"Price: {product['price']} | Stock: {product['stock']} units")
       
        if not alt_skus:
            print(f"{Colors.YELLOW}No alternatives found for this product.{Colors.ENDC}")
            return
       
        print(f"\n{Colors.BOLD}Alternative Options:{Colors.ENDC}")
        for i, alt_sku in enumerate(alt_skus, 1):
            if alt_sku in self.products:
                alt_product = self.products[alt_sku]
                print(f"\n{i}. {Colors.BOLD}{alt_product['name']}{Colors.ENDC} ({alt_sku})")
                print(f"   Price: {alt_product['price']} | Stock: {alt_product['stock']} units")
               
                # Highlight key differences (would be more sophisticated in real system)
                if alt_product['rating'] > product['rating']:
                    print(f"   {Colors.GREEN}★ Higher customer rating{Colors.ENDC}")
            else:
                print(f"{i}. {Colors.YELLOW}SKU: {alt_sku} (Product data not available){Colors.ENDC}")
               
        # Quick copy suggestion for email
        primary_alternative = product['name']
        if alt_skus and alt_skus[0] in self.products:
            suggestion = f"A great alternative to the {primary_alternative} is the product {self.products[alt_skus[0]]['name']}."
            print(f"\n{Colors.CYAN}Suggested text for customer email:{Colors.ENDC}")
            print(f"\"{suggestion}\"")

        # Add an option to view one of the alternative products
        print(f"\n{Colors.BOLD}COMMANDS:{Colors.ENDC}")
        print(f"{Colors.GREEN}[number]{Colors.ENDC} View product details")
        print(f"{Colors.GREEN}[B]{Colors.ENDC} Back to original product")
       
        command = input(f"\n{Colors.GREEN}Command:{Colors.ENDC} ").lower()
       
        # Inside display_alternatives method, where you display the selected product:
        if command.isdigit() and 1 <= int(command) <= len(alt_skus):
            selected_sku = alt_skus[int(command) - 1]
            if selected_sku in self.products:
                # Display the selected product and handle its options
                # Pass is_alternative=True to indicate this is an alternative product
                selected_product_sku = self.display_product(selected_sku, is_alternative=True)
                self.handle_product_options(selected_product_sku, is_alternative=True)
    
   
    def product_lookup(self):
        """Handle product lookup workflow"""
        query = input(f"\n{Colors.GREEN}Enter product name or ID:{Colors.ENDC} ")
        if not query.strip():
            return
       
        print(f"\nSearching for '{query}'...")
        time.sleep(0.5)  # Simulate search delay
       
        results = self.search_products(query)
        self.last_results = results
       
        if not results:
            print(f"{Colors.YELLOW}No products found matching '{query}'.{Colors.ENDC}")
            return
       
        while True:  # Loop to allow returning to search results
            print(f"\n{Colors.BOLD}Search Results:{Colors.ENDC}")
            for i, sku in enumerate(results[:3], 1):  # Show top 5 results
                if sku in self.products:
                    product = self.products[sku]
                    print(f"{i}. {product['name']} ({sku}) - {product['price']}")
                else:
                    print(f"{i}. Unknown product ({sku})")
           
            if len(results) > 3:
                print(f"...and {len(results) - 5} more results.")
           
            print(f"\n{Colors.BOLD}COMMANDS:{Colors.ENDC}")
            print(f"{Colors.GREEN}[number]{Colors.ENDC} View product details")
            print(f"{Colors.GREEN}[M]{Colors.ENDC} Return to main menu")
           
            choice = input(f"\n{Colors.GREEN}Select product number for details:{Colors.ENDC} ").lower()
           
            if choice == 'm':
                break  # Return to main menu
               
            if choice.isdigit() and 1 <= int(choice) <= len(results[:5]):
                selected_sku = results[int(choice) - 1]
                # Display the product and handle options
                product_sku = self.display_product(selected_sku)
                result = self.handle_product_options(product_sku)
               
                if result == 'menu':
                    break  # Return to main menu
                # For 'back', the loop continues and shows search results again
            else:
                print(f"{Colors.YELLOW}Invalid selection. Please try again.{Colors.ENDC}")
   
   
    def run(self):
        """Main loop of the widget"""
        while True:
            if self.widget_visible:
                self.clear_screen()
                self.display_header()
                self.display_menu()
           
            command = input(f"\n{Colors.GREEN}Command:{Colors.ENDC} ").lower()
           
            if command == 'q':
                break
            elif command == '/':
                self.widget_visible = not self.widget_visible
                if self.widget_visible:
                    print(f"{Colors.GREEN}Widget visible.{Colors.ENDC}")
                else:
                    print(f"{Colors.YELLOW}Widget hidden. Type '/' to show.{Colors.ENDC}")
            elif not self.widget_visible:
                if command == '/':
                    self.widget_visible = True
                continue
            elif command == 'p':
                self.product_lookup()
            else:
                print(f"{Colors.YELLOW}Invalid command. Please try again.{Colors.ENDC}")
           
            if self.widget_visible and command != '/':
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")




def main():
    """Main entry point for the widget"""
    widget = GraingerWidget()
   
    # Display welcome message
    print(f"{Colors.HEADER}{Colors.BOLD}Welcome to the Grainger Rep Assistant Widget!{Colors.ENDC}")
    print("This tool helps you quickly find product information while chatting with customers.")
    print(f"\n{Colors.BOLD}Loading widget...{Colors.ENDC}")
   
    # Simulate loading
    for i in range(5):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.2)
    print("\n")
   
    # Run the widget
    widget.run()
   
    print(f"\n{Colors.HEADER}Thank you for using the Grainger Rep Toolbar!{Colors.ENDC}")




if __name__ == "__main__":
    main()

