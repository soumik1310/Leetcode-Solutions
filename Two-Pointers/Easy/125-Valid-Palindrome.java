class Solution {
    public boolean isPalindrome(String s) {
        String str= s.toLowerCase();
        char ch[]= str.toCharArray();
        int left=0;
        int right= str.length()-1;

        while(right>left){
            if(Character.isLetterOrDigit(ch[left])==false){
                left++;
            }
            else if(Character.isLetterOrDigit(ch[right])==false){
                right--;
            }
            else if(ch[right]==ch[left]){
                right--;
                left++;
            }
            else{
                return false;
            }
        }
        return true;
    }
}