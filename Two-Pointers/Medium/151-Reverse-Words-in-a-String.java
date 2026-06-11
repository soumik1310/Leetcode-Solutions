class Solution {
    public String reverseWords(String s) {
        String w[]= s.trim().split("\\s+");
        String result="";

        for(int i=w.length-1; i>=0; i--){
            result+=w[i];
            if(i!=0)result=result+" ";
        }
        return result;
    }
}